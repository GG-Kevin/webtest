package com.kevinfamily.remoteassist.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.lifecycle.LifecycleService
import androidx.lifecycle.lifecycleScope
import com.kevinfamily.remoteassist.R
import com.kevinfamily.remoteassist.data.DeviceIdentity
import com.kevinfamily.remoteassist.data.Role
import com.kevinfamily.remoteassist.data.SessionRepository
import com.kevinfamily.remoteassist.ui.IncomingRequestActivity
import kotlinx.coroutines.launch

/**
 * Always-running foreground service that keeps a live Firestore listener open
 * so an incoming remote-support request is caught even while the app is in
 * the background. This is the app's substitute for a push-notification
 * backend: no FCM, no Cloud Functions, just a persistent listener.
 */
class WatchService : LifecycleService() {

    private val sessionRepository = SessionRepository()

    companion object {
        private const val CHANNEL_WATCH = "watch_status"
        private const val CHANNEL_REQUEST = "incoming_request"
        private const val NOTIF_ID_WATCH = 1
        private const val NOTIF_ID_REQUEST_BASE = 1000

        fun ensureStarted(context: Context) {
            val intent = Intent(context, WatchService::class.java)
            context.startForegroundService(intent)
        }
    }

    override fun onCreate() {
        super.onCreate()
        createChannels()
        startForeground(NOTIF_ID_WATCH, buildWatchNotification())
        observeIncomingRequestsIfChild()
    }

    override fun onStartCommand(intent: Intent, flags: Int, startId: Int): Int {
        super.onStartCommand(intent, flags, startId)
        return START_STICKY
    }

    private fun observeIncomingRequestsIfChild() {
        val role = DeviceIdentity.getRole(this)
        val myId = DeviceIdentity.getDeviceId(this)
        if (role != Role.CHILD || !DeviceIdentity.isPaired(this)) return

        lifecycleScope.launch {
            sessionRepository.listenForIncomingRequests(myId).collect { request ->
                showIncomingRequestNotification(request.sessionId, request.requesterId, request.requesterName)
            }
        }
    }

    private fun showIncomingRequestNotification(sessionId: String, requesterId: String, requesterName: String) {
        val openIntent = Intent(this, IncomingRequestActivity::class.java).apply {
            putExtra(IncomingRequestActivity.EXTRA_SESSION_ID, sessionId)
            putExtra(IncomingRequestActivity.EXTRA_REQUESTER_ID, requesterId)
            putExtra(IncomingRequestActivity.EXTRA_REQUESTER_NAME, requesterName)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        val pendingIntent = PendingIntent.getActivity(
            this, sessionId.hashCode(), openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val notification = NotificationCompat.Builder(this, CHANNEL_REQUEST)
            .setSmallIcon(R.drawable.ic_remote_support)
            .setContentTitle("$requesterName 님이 원격 지원을 요청했습니다")
            .setContentText("탭하여 승인 또는 거절하세요")
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_CALL)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setFullScreenIntent(pendingIntent, true)
            .build()

        val manager = getSystemService(NotificationManager::class.java)
        manager.notify(NOTIF_ID_REQUEST_BASE + sessionId.hashCode(), notification)
    }

    private fun buildWatchNotification(): Notification =
        NotificationCompat.Builder(this, CHANNEL_WATCH)
            .setSmallIcon(R.drawable.ic_remote_support)
            .setContentTitle("RemoteAssist 대기 중")
            .setContentText("가족 원격 지원 연결을 위해 실행 중입니다")
            .setPriority(NotificationCompat.PRIORITY_MIN)
            .setOngoing(true)
            .build()

    private fun createChannels() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(
            NotificationChannel(CHANNEL_WATCH, "대기 상태", NotificationManager.IMPORTANCE_MIN)
        )
        manager.createNotificationChannel(
            NotificationChannel(CHANNEL_REQUEST, "원격 지원 요청", NotificationManager.IMPORTANCE_HIGH)
        )
    }
}
