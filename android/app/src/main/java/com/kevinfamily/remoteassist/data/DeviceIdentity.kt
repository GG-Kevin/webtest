package com.kevinfamily.remoteassist.data

import android.content.Context
import java.util.UUID

/**
 * Local-only device state: a stable per-install device id, the chosen role
 * (parent/child), and the paired partner's device id once pairing succeeds.
 * Backed by SharedPreferences — nothing here touches the network.
 */
object DeviceIdentity {
    private const val PREFS = "device_identity"
    private const val KEY_DEVICE_ID = "device_id"
    private const val KEY_ROLE = "role"
    private const val KEY_PARTNER_ID = "partner_id"
    private const val KEY_DISPLAY_NAME = "display_name"

    private fun prefs(context: Context) =
        context.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun getDeviceId(context: Context): String {
        val p = prefs(context)
        p.getString(KEY_DEVICE_ID, null)?.let { return it }
        val generated = UUID.randomUUID().toString()
        p.edit().putString(KEY_DEVICE_ID, generated).apply()
        return generated
    }

    fun getRole(context: Context): Role? = Role.fromStringOrNull(prefs(context).getString(KEY_ROLE, null))

    fun setRole(context: Context, role: Role) {
        prefs(context).edit().putString(KEY_ROLE, role.name).apply()
    }

    fun getPartnerId(context: Context): String? = prefs(context).getString(KEY_PARTNER_ID, null)

    fun setPartnerId(context: Context, partnerId: String) {
        prefs(context).edit().putString(KEY_PARTNER_ID, partnerId).apply()
    }

    fun isPaired(context: Context): Boolean = getPartnerId(context) != null

    fun getDisplayName(context: Context): String =
        prefs(context).getString(KEY_DISPLAY_NAME, null) ?: (getRole(context)?.name ?: "Device")

    fun setDisplayName(context: Context, name: String) {
        prefs(context).edit().putString(KEY_DISPLAY_NAME, name).apply()
    }

    /** Clears role/pairing so the user can redo setup; keeps the device id stable. */
    fun resetPairing(context: Context) {
        prefs(context).edit().remove(KEY_ROLE).remove(KEY_PARTNER_ID).apply()
    }
}
