package com.kevinfamily.remoteassist.ui

import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.text.TextUtils
import androidx.appcompat.app.AppCompatActivity
import com.kevinfamily.remoteassist.data.DeviceIdentity
import com.kevinfamily.remoteassist.data.Role
import com.kevinfamily.remoteassist.databinding.ActivityMainBinding
import com.kevinfamily.remoteassist.service.RemoteInputAccessibilityService
import com.kevinfamily.remoteassist.service.WatchService

/**
 * Entry point. Routes the user to role selection, pairing, or the
 * role-appropriate home screen depending on locally saved state.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.btnRoleParent.setOnClickListener { startPairing(Role.PARENT) }
        binding.btnRoleChild.setOnClickListener { startPairing(Role.CHILD) }
        binding.btnResetPairing.setOnClickListener {
            DeviceIdentity.resetPairing(this)
            render()
        }
    }

    override fun onResume() {
        super.onResume()
        render()
    }

    private fun startPairing(role: Role) {
        DeviceIdentity.setRole(this, role)
        startActivity(Intent(this, PairingActivity::class.java))
    }

    private fun render() {
        val role = DeviceIdentity.getRole(this)
        val paired = DeviceIdentity.isPaired(this)

        if (role == null) {
            binding.roleGroup.visibility = android.view.View.VISIBLE
            binding.statusGroup.visibility = android.view.View.GONE
            return
        }
        if (!paired) {
            startActivity(Intent(this, PairingActivity::class.java))
            return
        }

        binding.roleGroup.visibility = android.view.View.GONE
        binding.statusGroup.visibility = android.view.View.VISIBLE

        // Keep the always-on Firestore listener running regardless of role.
        WatchService.ensureStarted(this)

        when (role) {
            Role.PARENT -> {
                binding.statusText.text = "부모 기기로 설정됨. 자녀 기기에 도움이 필요할 때 아래 버튼으로 원격 지원을 요청하세요."
                binding.btnPrimaryAction.text = "원격 지원 요청"
                binding.btnPrimaryAction.visibility = android.view.View.VISIBLE
                binding.btnAccessibilitySettings.visibility = android.view.View.GONE
                binding.btnPrimaryAction.setOnClickListener {
                    startActivity(Intent(this, ParentControlActivity::class.java))
                }
            }
            Role.CHILD -> {
                val accessibilityOn = isAccessibilityServiceEnabled()
                binding.statusText.text = if (accessibilityOn) {
                    "대기 중입니다. 부모님이 원격 지원을 요청하면 알림이 표시됩니다."
                } else {
                    "마지막 설정이 남았습니다: 원격 입력을 받으려면 접근성 서비스를 켜주세요."
                }
                binding.btnPrimaryAction.visibility = android.view.View.GONE
                binding.btnAccessibilitySettings.visibility =
                    if (accessibilityOn) android.view.View.GONE else android.view.View.VISIBLE
                binding.btnAccessibilitySettings.setOnClickListener {
                    startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
                }
            }
        }
    }

    private fun isAccessibilityServiceEnabled(): Boolean {
        val expected = ComponentNameHelper.name(this, RemoteInputAccessibilityService::class.java)
        val enabledServices = Settings.Secure.getString(
            contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        ) ?: return false
        return TextUtils.SimpleStringSplitter(':').apply { setString(enabledServices) }
            .asSequence()
            .any { it.equals(expected, ignoreCase = true) }
    }
}

private object ComponentNameHelper {
    fun name(context: android.content.Context, cls: Class<*>): String =
        android.content.ComponentName(context, cls).flattenToString()
}

private fun TextUtils.SimpleStringSplitter.asSequence(): Sequence<String> = sequence {
    while (hasNext()) yield(next())
}
