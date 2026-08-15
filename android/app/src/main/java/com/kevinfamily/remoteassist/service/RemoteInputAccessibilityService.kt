package com.kevinfamily.remoteassist.service

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.graphics.Path
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import com.kevinfamily.remoteassist.data.RemoteInputCommand

/**
 * Executes remote-input commands from the paired parent device. Only ever
 * acts while a session is active — commands arrive exclusively through
 * ScreenCaptureService's WebRTC data channel, which only exists during an
 * approved session, so there's no separate "am I allowed" check needed here.
 */
class RemoteInputAccessibilityService : AccessibilityService() {

    companion object {
        var instance: RemoteInputAccessibilityService? = null
            private set
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
    }

    override fun onDestroy() {
        super.onDestroy()
        if (instance === this) instance = null
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {}
    override fun onInterrupt() {}

    fun execute(command: RemoteInputCommand) {
        when (command) {
            is RemoteInputCommand.Tap -> tap(command.x, command.y)
            is RemoteInputCommand.Swipe -> swipe(command.x1, command.y1, command.x2, command.y2, command.durationMs)
            is RemoteInputCommand.TypeText -> typeText(command.text)
            RemoteInputCommand.Back -> performGlobalAction(GLOBAL_ACTION_BACK)
            RemoteInputCommand.Home -> performGlobalAction(GLOBAL_ACTION_HOME)
        }
    }

    private fun tap(nx: Float, ny: Float) {
        val (x, y) = toPixels(nx, ny)
        val path = Path().apply { moveTo(x, y) }
        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, 60))
            .build()
        dispatchGesture(gesture, null, null)
    }

    private fun swipe(nx1: Float, ny1: Float, nx2: Float, ny2: Float, durationMs: Long) {
        val (x1, y1) = toPixels(nx1, ny1)
        val (x2, y2) = toPixels(nx2, ny2)
        val path = Path().apply {
            moveTo(x1, y1)
            lineTo(x2, y2)
        }
        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, durationMs.coerceAtLeast(50)))
            .build()
        dispatchGesture(gesture, null, null)
    }

    private fun typeText(text: String) {
        val focused = rootInActiveWindow?.findFocus(AccessibilityNodeInfo.FOCUS_INPUT) ?: return
        val args = Bundle().apply {
            putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
        }
        focused.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
        focused.recycle()
    }

    private fun toPixels(nx: Float, ny: Float): Pair<Float, Float> {
        val metrics = resources.displayMetrics
        return (nx.coerceIn(0f, 1f) * metrics.widthPixels) to (ny.coerceIn(0f, 1f) * metrics.heightPixels)
    }
}
