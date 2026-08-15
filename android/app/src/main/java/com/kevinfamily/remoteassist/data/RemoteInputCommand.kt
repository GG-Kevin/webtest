package com.kevinfamily.remoteassist.data

import org.json.JSONObject

/**
 * Wire format sent over the WebRTC data channel. Coordinates are normalized
 * to 0..1 (fraction of screen width/height) so the parent's rendered video
 * size never has to match the child's actual screen resolution.
 */
sealed class RemoteInputCommand {
    data class Tap(val x: Float, val y: Float) : RemoteInputCommand()
    data class Swipe(val x1: Float, val y1: Float, val x2: Float, val y2: Float, val durationMs: Long) :
        RemoteInputCommand()
    data class TypeText(val text: String) : RemoteInputCommand()
    object Back : RemoteInputCommand()
    object Home : RemoteInputCommand()

    fun toJson(): String {
        val obj = JSONObject()
        when (this) {
            is Tap -> obj.put("type", "tap").put("x", x).put("y", y)
            is Swipe -> obj.put("type", "swipe").put("x1", x1).put("y1", y1)
                .put("x2", x2).put("y2", y2).put("durationMs", durationMs)
            is TypeText -> obj.put("type", "text").put("text", text)
            Back -> obj.put("type", "back")
            Home -> obj.put("type", "home")
        }
        return obj.toString()
    }

    companion object {
        fun fromJson(raw: String): RemoteInputCommand? = runCatching {
            val obj = JSONObject(raw)
            when (obj.getString("type")) {
                "tap" -> Tap(obj.getDouble("x").toFloat(), obj.getDouble("y").toFloat())
                "swipe" -> Swipe(
                    obj.getDouble("x1").toFloat(), obj.getDouble("y1").toFloat(),
                    obj.getDouble("x2").toFloat(), obj.getDouble("y2").toFloat(),
                    obj.optLong("durationMs", 300L)
                )
                "text" -> TypeText(obj.getString("text"))
                "back" -> Back
                "home" -> Home
                else -> null
            }
        }.getOrNull()
    }
}
