package com.kevinfamily.remoteassist.ui

import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.kevinfamily.remoteassist.data.DeviceIdentity
import com.kevinfamily.remoteassist.data.PairingRepository
import com.kevinfamily.remoteassist.data.Role
import com.kevinfamily.remoteassist.databinding.ActivityPairingBinding
import kotlinx.coroutines.launch

/**
 * Parent side: generates a 6-digit code and waits for the child to enter it.
 * Child side: takes a code and claims it.
 * Either way, success stores the partner's device id locally and returns to MainActivity.
 */
class PairingActivity : AppCompatActivity() {

    private lateinit var binding: ActivityPairingBinding
    private val repo = PairingRepository()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPairingBinding.inflate(layoutInflater)
        setContentView(binding.root)

        when (DeviceIdentity.getRole(this)) {
            Role.PARENT -> setUpAsParent()
            Role.CHILD -> setUpAsChild()
            null -> finish()
        }
    }

    private fun setUpAsParent() {
        binding.instructionText.text = "자녀 기기의 앱에 아래 코드를 입력하게 해주세요. (10분 내 유효)"
        binding.codeInputGroup.visibility = View.GONE
        binding.codeDisplay.visibility = View.VISIBLE
        binding.progressBar.visibility = View.VISIBLE

        val myId = DeviceIdentity.getDeviceId(this)
        lifecycleScope.launch {
            val code = repo.createPairingCode(myId)
            binding.codeDisplay.text = code
            repo.awaitChildJoin(code).collect { childId ->
                completePairing(childId)
            }
        }
    }

    private fun setUpAsChild() {
        binding.instructionText.text = "부모님 기기 화면에 표시된 6자리 코드를 입력하세요."
        binding.codeDisplay.visibility = View.GONE
        binding.codeInputGroup.visibility = View.VISIBLE

        binding.btnSubmitCode.setOnClickListener {
            val code = binding.codeInput.text?.toString()?.trim().orEmpty()
            if (code.length != 6) {
                binding.instructionText.text = "6자리 코드를 정확히 입력해주세요."
                return@setOnClickListener
            }
            binding.progressBar.visibility = View.VISIBLE
            binding.btnSubmitCode.isEnabled = false
            val myId = DeviceIdentity.getDeviceId(this)
            lifecycleScope.launch {
                val parentId = repo.claimPairingCode(code, myId)
                if (parentId == null) {
                    binding.progressBar.visibility = View.GONE
                    binding.btnSubmitCode.isEnabled = true
                    binding.instructionText.text = "코드가 유효하지 않거나 만료되었습니다. 다시 확인해주세요."
                } else {
                    completePairing(parentId)
                }
            }
        }
    }

    private suspend fun completePairing(partnerId: String) {
        val myId = DeviceIdentity.getDeviceId(this)
        val role = DeviceIdentity.getRole(this) ?: return
        DeviceIdentity.setPartnerId(this, partnerId)
        repo.saveDeviceRecord(myId, role, partnerId, DeviceIdentity.getDisplayName(this))
        finish()
    }
}
