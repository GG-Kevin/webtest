package com.kevinfamily.remoteassist.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.media.projection.MediaProjection
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.lifecycle.LifecycleService
import androidx.lifecycle.lifecycleScope
import com.kevinfamily.remoteassist.R
import com.kevinfamily.remoteassist.data.RemoteInputCommand
import com.kevinfamily.remoteassist.data.SessionRepository
import com.kevinfamily.remoteassist.data.SessionStatus
import com.kevinfamily.remoteassist.webrtc.WebRtcClient
import kotlinx.coroutines.launch
import org.webrtc.ScreenCapturerAndroid
import org.webrtc.SurfaceTextureHelper
import org.webrtc.VideoCapturer

/**
 * Child-side session runtime: captures the screen (MediaProjection) into a
 * WebRTC video track, answers the parent's offer, exchanges ICE candidates,
 * and forwards incoming data-channel commands to the accessibility service.
 * Lives only for the duration of one approved session.
 */
class ScreenCaptureService : LifecycleService() {

    private val sessionRepository = SessionRepository()
    private var webRtcClient: WebRtcClient? = null
    private var capturer: VideoCapturer? = null

    companion object {
        private const val CHANNEL_ACTIVE = "active_session"
        private const val NOTIF_ID = 2

        private const val EXTRA_SESSION_ID = "session_id"
        private const val EXTRA_PARENT_ID = "parent_id"
        private const val EXTRA_RESULT_CODE = "result_code"
        private const val EXTRA_PROJECTION_DATA = "projection_data"

        fun start(context: Context, sessionId: String, parentId: String, resultCode: Int, projectionData: Intent) {
            val intent = Intent(context, ScreenCaptureService::class.java).apply {
                putExtra(EXTRA_SESSION_ID, sessionId)
                putExtra(EXTRA_PARENT_ID, parentId)
                putExtra(EXTRA_RESULT_CODE, resultCode)
                putExtra(EXTRA_PROJECTION_DATA, projectionData)
            }
            context.startForegroundService(intent)
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, ScreenCaptureService::class.java))
        }
    }

    override fun onCreate() {
        super.onCreate()
        createChannel()
        startForeground(NOTIF_ID, buildNotification())
    }

    override fun onStartCommand(intent: Intent, flags: Int, startId: Int): Int {
        super.onStartCommand(intent, flags, startId)
        val sessionId = intent.getStringExtra(EXTRA_SESSION_ID)
        val parentId = intent.getStringExtra(EXTRA_PARENT_ID)
        val resultCode = intent.getIntExtra(EXTRA_RESULT_CODE, 0)
        val projectionData = intent.getParcelableExtra<Intent>(EXTRA_PROJECTION_DATA)
        if (sessionId != null && parentId != null && projectionData != null) {
            beginSession(sessionId, parentId, resultCode, projectionData)
        } else {
            stopSelf()
        }
        return START_NOT_STICKY
    }

    private fun beginSession(sessionId: String, parentId: String, resultCode: Int, projectionData: Intent) {
        val client = WebRtcClient(applicationContext).also { webRtcClient = it }

        client.onLocalIceCandidate = { candidate ->
            lifecycleScope.launch { sessionRepository.addIceCandidate(sessionId, fromCaller = false, candidate) }
        }
        client.onControlMessage = { raw ->
            RemoteInputCommand.fromJson(raw)?.let { RemoteInputAccessibilityService.instance?.execute(it) }
        }

        client.open()
        startScreenCapture(client, resultCode, projectionData)

        lifecycleScope.launch {
            sessionRepository.listenOffer(sessionId).collect { offerSdp ->
                client.handleOfferAndCreateAnswer(offerSdp) { answerSdp ->
                    lifecycleScope.launch { sessionRepository.sendAnswer(sessionId, answerSdp) }
                }
            }
        }
        lifecycleScope.launch {
            sessionRepository.listenIceCandidates(sessionId, fromCaller = true).collect { candidate ->
                client.addRemoteIceCandidate(candidate)
            }
        }
        lifecycleScope.launch {
            sessionRepository.listenStatus(sessionId).collect { status ->
                if (status == SessionStatus.ENDED || status == SessionStatus.DECLINED) {
                    endSession()
                }
            }
        }
    }

    private fun startScreenCapture(client: WebRtcClient, resultCode: Int, projectionData: Intent) {
        val screenCapturer = ScreenCapturerAndroid(
            projectionData,
            object : MediaProjection.Callback() {
                override fun onStop() {
                    endSession()
                }
            }
        )
        capturer = screenCapturer

        val factory = client.peerConnectionFactory()
        val videoSource = factory.createVideoSource(true)
        val surfaceTextureHelper = SurfaceTextureHelper.create("ScreenCaptureThread", client.eglBase.eglBaseContext)
        screenCapturer.initialize(surfaceTextureHelper, applicationContext, videoSource.capturerObserver)

        val metrics = resources.displayMetrics
        screenCapturer.startCapture(metrics.widthPixels, metrics.heightPixels, 15)

        val videoTrack = factory.createVideoTrack("screen0", videoSource)
        client.attachLocalVideoTrack(videoTrack)
    }

    private fun endSession() {
        capturer?.let { runCatching { it.stopCapture() } }
        capturer?.dispose()
        capturer = null
        webRtcClient?.close()
        webRtcClient = null
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    override fun onDestroy() {
        endSession()
        super.onDestroy()
    }

    private fun buildNotification(): Notification =
        NotificationCompat.Builder(this, CHANNEL_ACTIVE)
            .setSmallIcon(R.drawable.ic_remote_support)
            .setContentTitle("원격 지원 세션이 진행 중입니다")
            .setContentText("화면이 부모님 기기와 공유되고 있습니다")
            .setOngoing(true)
            .build()

    private fun createChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(
            NotificationChannel(CHANNEL_ACTIVE, "활성 세션", NotificationManager.IMPORTANCE_LOW)
        )
    }
}
