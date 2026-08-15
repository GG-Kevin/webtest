package com.kevinfamily.remoteassist.ui

import android.os.Bundle
import android.view.MotionEvent
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.kevinfamily.remoteassist.data.DeviceIdentity
import com.kevinfamily.remoteassist.data.RemoteInputCommand
import com.kevinfamily.remoteassist.data.SessionRepository
import com.kevinfamily.remoteassist.data.SessionStatus
import com.kevinfamily.remoteassist.databinding.ActivityParentControlBinding
import com.kevinfamily.remoteassist.webrtc.WebRtcClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import org.webrtc.RendererCommon
import org.webrtc.VideoTrack

/**
 * Parent side: sends a session request, waits for the child's approval, then
 * renders the shared screen and turns touches on the video view into
 * normalized remote-input commands sent over the data channel.
 */
class ParentControlActivity : AppCompatActivity() {

    private lateinit var binding: ActivityParentControlBinding
    private val sessionRepository = SessionRepository()
    private var webRtcClient: WebRtcClient? = null
    private var remoteVideoTrack: VideoTrack? = null
    private var sessionId: String? = null
    private var touchDownX = 0f
    private var touchDownY = 0f
    private var touchDownTime = 0L

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityParentControlBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.statusText.text = "원격 지원을 요청하는 중..."
        binding.controlsGroup.visibility = View.GONE

        binding.btnBack.setOnClickListener { send(RemoteInputCommand.Back) }
        binding.btnHome.setOnClickListener { send(RemoteInputCommand.Home) }
        binding.btnSendText.setOnClickListener {
            val text = binding.textInput.text?.toString().orEmpty()
            if (text.isNotEmpty()) {
                send(RemoteInputCommand.TypeText(text))
                binding.textInput.text?.clear()
            }
        }
        binding.btnEndSession.setOnClickListener { finish() }

        binding.remoteView.setOnTouchListener { view, event -> handleTouch(view, event) }

        requestSession()
    }

    private fun requestSession() {
        val myId = DeviceIdentity.getDeviceId(this)
        val partnerId = DeviceIdentity.getPartnerId(this) ?: return finish()
        val myName = DeviceIdentity.getDisplayName(this)

        lifecycleScope.launch {
            val id = sessionRepository.createRequest(myId, myName, partnerId)
            sessionId = id
            sessionRepository.listenStatus(id).collect { status ->
                when (status) {
                    SessionStatus.ACCEPTED -> onAccepted(id)
                    SessionStatus.DECLINED -> {
                        binding.statusText.text = "자녀가 요청을 거절했습니다."
                    }
                    SessionStatus.ENDED -> {
                        binding.statusText.text = "세션이 종료되었습니다."
                        teardownWebRtc()
                    }
                    SessionStatus.REQUESTED -> Unit
                }
            }
        }
    }

    private fun onAccepted(sessionId: String) {
        binding.statusText.text = "연결하는 중..."

        val client = WebRtcClient(this).also { webRtcClient = it }
        binding.remoteView.init(client.eglBase.eglBaseContext, null)
        binding.remoteView.setScalingType(RendererCommon.ScalingType.SCALE_ASPECT_FIT)

        client.onLocalIceCandidate = { candidate ->
            lifecycleScope.launch { sessionRepository.addIceCandidate(sessionId, fromCaller = true, candidate) }
        }
        client.onRemoteVideoTrack = { track ->
            remoteVideoTrack = track
            runOnUiThread { track.addSink(binding.remoteView) }
        }
        client.onDataChannelReady = {
            runOnUiThread {
                binding.statusText.text = "연결됨"
                binding.controlsGroup.visibility = View.VISIBLE
            }
        }

        client.open()
        client.createOffer { sdp ->
            lifecycleScope.launch { sessionRepository.sendOffer(sessionId, sdp) }
        }

        lifecycleScope.launch {
            sessionRepository.listenAnswer(sessionId).collect { sdp -> client.applyRemoteAnswer(sdp) }
        }
        lifecycleScope.launch {
            sessionRepository.listenIceCandidates(sessionId, fromCaller = false).collect { candidate ->
                client.addRemoteIceCandidate(candidate)
            }
        }
    }

    private fun handleTouch(view: View, event: MotionEvent): Boolean {
        val nx = (event.x / view.width).coerceIn(0f, 1f)
        val ny = (event.y / view.height).coerceIn(0f, 1f)
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                touchDownX = nx
                touchDownY = ny
                touchDownTime = System.currentTimeMillis()
            }
            MotionEvent.ACTION_UP -> {
                val elapsed = System.currentTimeMillis() - touchDownTime
                val moved = kotlin.math.hypot((nx - touchDownX).toDouble(), (ny - touchDownY).toDouble())
                if (moved < 0.02) {
                    send(RemoteInputCommand.Tap(nx, ny))
                } else {
                    send(RemoteInputCommand.Swipe(touchDownX, touchDownY, nx, ny, elapsed.coerceIn(50, 1500)))
                }
            }
        }
        return true
    }

    private fun send(command: RemoteInputCommand) {
        webRtcClient?.sendControlMessage(command.toJson())
    }

    private fun teardownWebRtc() {
        webRtcClient?.close()
        webRtcClient = null
    }

    override fun onDestroy() {
        // lifecycleScope is cancelled the instant ON_DESTROY dispatches, which can race
        // this write; use a short-lived unstructured scope so the Firestore update lands.
        sessionId?.let { id -> CoroutineScope(Dispatchers.IO).launch { sessionRepository.endSession(id) } }
        teardownWebRtc()
        super.onDestroy()
    }
}
