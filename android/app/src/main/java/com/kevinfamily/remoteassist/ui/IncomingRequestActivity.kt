package com.kevinfamily.remoteassist.ui

import android.content.Intent
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Bundle
import android.view.WindowManager
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.kevinfamily.remoteassist.data.SessionRepository
import com.kevinfamily.remoteassist.databinding.ActivityIncomingRequestBinding
import com.kevinfamily.remoteassist.service.ScreenCaptureService
import kotlinx.coroutines.launch

/**
 * Child-side approve/decline prompt for an incoming remote-support request.
 * Approving immediately triggers Android's own screen-capture consent dialog
 * (MediaProjection) — a second, OS-level confirmation the user always sees.
 */
class IncomingRequestActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_SESSION_ID = "session_id"
        const val EXTRA_REQUESTER_ID = "requester_id"
        const val EXTRA_REQUESTER_NAME = "requester_name"
    }

    private lateinit var binding: ActivityIncomingRequestBinding
    private val sessionRepository = SessionRepository()

    private lateinit var sessionId: String
    private lateinit var requesterId: String

    private val projectionLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        val data = result.data
        if (result.resultCode == RESULT_OK && data != null) {
            ScreenCaptureService.start(this, sessionId, requesterId, result.resultCode, data)
        }
        finish()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        showOverLockScreenAndWake()
        binding = ActivityIncomingRequestBinding.inflate(layoutInflater)
        setContentView(binding.root)

        sessionId = intent.getStringExtra(EXTRA_SESSION_ID) ?: return finish()
        requesterId = intent.getStringExtra(EXTRA_REQUESTER_ID) ?: return finish()
        val requesterName = intent.getStringExtra(EXTRA_REQUESTER_NAME) ?: "부모"

        binding.requesterText.text = "$requesterName 님이 원격 지원을 요청했습니다.\n승인하면 화면 공유 및 조작 권한이 상대에게 전달됩니다."

        binding.btnAccept.setOnClickListener { onAccept() }
        binding.btnDecline.setOnClickListener { onDecline() }
    }

    private fun onAccept() {
        lifecycleScope.launch {
            sessionRepository.respond(sessionId, accept = true)
            val projectionManager = getSystemService(MediaProjectionManager::class.java)
            projectionLauncher.launch(projectionManager.createScreenCaptureIntent())
        }
    }

    private fun showOverLockScreenAndWake() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
            setShowWhenLocked(true)
            setTurnScreenOn(true)
        } else {
            @Suppress("DEPRECATION")
            window.addFlags(
                WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED or
                    WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON or
                    WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON
            )
        }
    }

    private fun onDecline() {
        lifecycleScope.launch {
            sessionRepository.respond(sessionId, accept = false)
            finish()
        }
    }
}
