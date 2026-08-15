package com.kevinfamily.remoteassist

import android.app.Application
import org.webrtc.PeerConnectionFactory

class RemoteAssistApp : Application() {
    override fun onCreate() {
        super.onCreate()
        PeerConnectionFactory.initialize(
            PeerConnectionFactory.InitializationOptions.builder(this)
                .setEnableInternalTracer(false)
                .createInitializationOptions()
        )
    }
}
