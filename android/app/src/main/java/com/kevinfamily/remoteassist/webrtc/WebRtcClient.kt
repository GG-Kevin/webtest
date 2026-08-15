package com.kevinfamily.remoteassist.webrtc

import android.content.Context
import com.kevinfamily.remoteassist.data.IceCandidateData
import org.webrtc.DataChannel
import org.webrtc.DefaultVideoDecoderFactory
import org.webrtc.DefaultVideoEncoderFactory
import org.webrtc.EglBase
import org.webrtc.IceCandidate
import org.webrtc.MediaConstraints
import org.webrtc.MediaStream
import org.webrtc.PeerConnection
import org.webrtc.PeerConnectionFactory
import org.webrtc.RtpReceiver
import org.webrtc.SdpObserver
import org.webrtc.SessionDescription
import org.webrtc.VideoTrack
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets

/**
 * Thin wrapper around a single WebRTC PeerConnection covering exactly what
 * this app needs: one video track (child's captured screen, callee side)
 * and one data channel (remote-input commands, caller-created). Signaling
 * (SDP/ICE exchange) is handled by the caller of this class via callbacks —
 * this file has no knowledge of Firestore.
 */
class WebRtcClient(context: Context) {

    val eglBase: EglBase = EglBase.create()

    private val factory: PeerConnectionFactory = PeerConnectionFactory.builder()
        .setVideoEncoderFactory(DefaultVideoEncoderFactory(eglBase.eglBaseContext, true, true))
        .setVideoDecoderFactory(DefaultVideoDecoderFactory(eglBase.eglBaseContext))
        .createPeerConnectionFactory()

    private var peerConnection: PeerConnection? = null
    private var dataChannel: DataChannel? = null

    var onLocalIceCandidate: ((IceCandidateData) -> Unit)? = null
    var onRemoteVideoTrack: ((VideoTrack) -> Unit)? = null
    var onControlMessage: ((String) -> Unit)? = null
    var onDataChannelReady: (() -> Unit)? = null

    fun peerConnectionFactory(): PeerConnectionFactory = factory

    /** Default public STUN only. Add a TURN server here if connections fail over cellular data. */
    fun defaultIceServers(): List<PeerConnection.IceServer> = listOf(
        PeerConnection.IceServer.builder("stun:stun.l.google.com:19302").createIceServer(),
        PeerConnection.IceServer.builder("stun:stun1.l.google.com:19302").createIceServer()
    )

    fun open(iceServers: List<PeerConnection.IceServer> = defaultIceServers()) {
        val config = PeerConnection.RTCConfiguration(iceServers).apply {
            sdpSemantics = PeerConnection.SdpSemantics.UNIFIED_PLAN
        }
        peerConnection = factory.createPeerConnection(config, object : PeerConnection.Observer {
            override fun onIceCandidate(candidate: IceCandidate) {
                onLocalIceCandidate?.invoke(
                    IceCandidateData(candidate.sdpMid, candidate.sdpMLineIndex, candidate.sdp)
                )
            }

            override fun onAddTrack(receiver: RtpReceiver, mediaStreams: Array<out MediaStream>) {
                (receiver.track() as? VideoTrack)?.let { onRemoteVideoTrack?.invoke(it) }
            }

            override fun onDataChannel(channel: DataChannel) {
                dataChannel = channel
                attachDataChannelObserver(channel)
            }

            override fun onIceConnectionChange(state: PeerConnection.IceConnectionState) {}
            override fun onIceConnectionReceivingChange(receiving: Boolean) {}
            override fun onIceGatheringChange(state: PeerConnection.IceGatheringState) {}
            override fun onIceCandidatesRemoved(candidates: Array<out IceCandidate>) {}
            override fun onSignalingChange(state: PeerConnection.SignalingState) {}
            override fun onAddStream(stream: MediaStream) {}
            override fun onRemoveStream(stream: MediaStream) {}
            override fun onRenegotiationNeeded() {}
        })
    }

    /** Callee (child) side: attach the screen-capture video track before answering. */
    fun attachLocalVideoTrack(videoTrack: VideoTrack) {
        peerConnection?.addTrack(videoTrack, listOf("screen_stream"))
    }

    /** Caller (parent) side: opens the data channel and produces an SDP offer. */
    fun createOffer(onSdpReady: (String) -> Unit) {
        val channel = peerConnection?.createDataChannel("control", DataChannel.Init())
        dataChannel = channel
        attachDataChannelObserver(channel)

        peerConnection?.createOffer(object : SimpleSdpObserver() {
            override fun onCreateSuccess(sdp: SessionDescription) {
                peerConnection?.setLocalDescription(SimpleSdpObserver(), sdp)
                onSdpReady(sdp.description)
            }
        }, MediaConstraints())
    }

    /** Callee (child) side: apply the offer and produce an SDP answer. */
    fun handleOfferAndCreateAnswer(remoteSdp: String, onSdpReady: (String) -> Unit) {
        peerConnection?.setRemoteDescription(
            SimpleSdpObserver(), SessionDescription(SessionDescription.Type.OFFER, remoteSdp)
        )
        peerConnection?.createAnswer(object : SimpleSdpObserver() {
            override fun onCreateSuccess(sdp: SessionDescription) {
                peerConnection?.setLocalDescription(SimpleSdpObserver(), sdp)
                onSdpReady(sdp.description)
            }
        }, MediaConstraints())
    }

    /** Caller (parent) side: apply the answer once it arrives. */
    fun applyRemoteAnswer(remoteSdp: String) {
        peerConnection?.setRemoteDescription(
            SimpleSdpObserver(), SessionDescription(SessionDescription.Type.ANSWER, remoteSdp)
        )
    }

    fun addRemoteIceCandidate(data: IceCandidateData) {
        peerConnection?.addIceCandidate(IceCandidate(data.sdpMid, data.sdpMLineIndex, data.sdp))
    }

    fun sendControlMessage(text: String) {
        val buffer = DataChannel.Buffer(ByteBuffer.wrap(text.toByteArray(StandardCharsets.UTF_8)), false)
        dataChannel?.send(buffer)
    }

    private fun attachDataChannelObserver(channel: DataChannel?) {
        channel?.registerObserver(object : DataChannel.Observer {
            override fun onBufferedAmountChange(previousAmount: Long) {}

            override fun onStateChange() {
                if (channel.state() == DataChannel.State.OPEN) onDataChannelReady?.invoke()
            }

            override fun onMessage(buffer: DataChannel.Buffer) {
                val bytes = ByteArray(buffer.data.remaining())
                buffer.data.get(bytes)
                onControlMessage?.invoke(String(bytes, StandardCharsets.UTF_8))
            }
        })
    }

    fun close() {
        dataChannel?.close()
        dataChannel = null
        peerConnection?.close()
        peerConnection = null
        eglBase.release()
    }
}

private abstract class SimpleSdpObserver : SdpObserver {
    override fun onCreateSuccess(sdp: SessionDescription) {}
    override fun onSetSuccess() {}
    override fun onCreateFailure(error: String) {}
    override fun onSetFailure(error: String) {}
}
