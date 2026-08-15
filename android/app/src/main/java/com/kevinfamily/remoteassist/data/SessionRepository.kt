package com.kevinfamily.remoteassist.data

import com.google.firebase.firestore.DocumentSnapshot
import com.google.firebase.firestore.FieldValue
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.Query
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.tasks.await

enum class SessionStatus { REQUESTED, ACCEPTED, DECLINED, ENDED;

    companion object {
        fun fromStringOrNull(value: String?): SessionStatus? = entries.firstOrNull { it.name == value }
    }
}

data class SessionRequest(
    val sessionId: String,
    val requesterId: String,
    val requesterName: String
)

/** A single ICE candidate, mirrored as a plain map for Firestore. */
data class IceCandidateData(
    val sdpMid: String?,
    val sdpMLineIndex: Int,
    val sdp: String
)

/**
 * Firestore-backed session lifecycle (request -> accept/decline -> active -> ended)
 * plus the WebRTC signaling documents exchanged during an active session.
 * No custom backend: everything here is a Firestore read/write or realtime listener.
 */
class SessionRepository(
    private val db: FirebaseFirestore = FirebaseFirestore.getInstance()
) {
    private val sessions get() = db.collection("sessions")

    suspend fun createRequest(requesterId: String, requesterName: String, targetId: String): String {
        val doc = sessions.document()
        doc.set(
            mapOf(
                "requesterId" to requesterId,
                "requesterName" to requesterName,
                "targetId" to targetId,
                "status" to SessionStatus.REQUESTED.name,
                "createdAt" to FieldValue.serverTimestamp()
            )
        ).await()
        return doc.id
    }

    /** Child side: live stream of pending requests addressed to this device. */
    fun listenForIncomingRequests(myDeviceId: String): Flow<SessionRequest> = callbackFlow {
        val registration = sessions
            .whereEqualTo("targetId", myDeviceId)
            .whereEqualTo("status", SessionStatus.REQUESTED.name)
            .orderBy("createdAt", Query.Direction.DESCENDING)
            .addSnapshotListener { snapshot, error ->
                if (error != null) return@addSnapshotListener
                snapshot?.documentChanges?.forEach { change ->
                    if (change.type == com.google.firebase.firestore.DocumentChange.Type.ADDED) {
                        val doc = change.document
                        trySend(
                            SessionRequest(
                                sessionId = doc.id,
                                requesterId = doc.getString("requesterId").orEmpty(),
                                requesterName = doc.getString("requesterName") ?: "부모"
                            )
                        )
                    }
                }
            }
        awaitClose { registration.remove() }
    }

    suspend fun respond(sessionId: String, accept: Boolean) {
        sessions.document(sessionId)
            .update("status", if (accept) SessionStatus.ACCEPTED.name else SessionStatus.DECLINED.name)
            .await()
    }

    suspend fun endSession(sessionId: String) {
        sessions.document(sessionId).update("status", SessionStatus.ENDED.name).await()
    }

    /** Parent side: watch a session it created to learn accept/decline/end transitions. */
    fun listenStatus(sessionId: String): Flow<SessionStatus> = callbackFlow {
        val registration = sessions.document(sessionId).addSnapshotListener { snapshot, error ->
            if (error != null) return@addSnapshotListener
            SessionStatus.fromStringOrNull(snapshot?.getString("status"))?.let { trySend(it) }
        }
        awaitClose { registration.remove() }
    }

    // --- WebRTC signaling, scoped under sessions/{id}/signaling/{offer,answer} ---

    suspend fun sendOffer(sessionId: String, sdp: String) = putSdp(sessionId, "offer", sdp)
    suspend fun sendAnswer(sessionId: String, sdp: String) = putSdp(sessionId, "answer", sdp)

    private suspend fun putSdp(sessionId: String, doc: String, sdp: String) {
        sessions.document(sessionId).collection("signaling").document(doc)
            .set(mapOf("sdp" to sdp)).await()
    }

    fun listenOffer(sessionId: String): Flow<String> = listenSdp(sessionId, "offer")
    fun listenAnswer(sessionId: String): Flow<String> = listenSdp(sessionId, "answer")

    private fun listenSdp(sessionId: String, doc: String): Flow<String> = callbackFlow {
        val registration = sessions.document(sessionId).collection("signaling").document(doc)
            .addSnapshotListener { snapshot, error ->
                if (error != null) return@addSnapshotListener
                snapshot?.getString("sdp")?.let { trySend(it) }
            }
        awaitClose { registration.remove() }
    }

    /** [fromCaller] = true for the requester's (parent's) candidates, false for the target's (child's). */
    suspend fun addIceCandidate(sessionId: String, fromCaller: Boolean, candidate: IceCandidateData) {
        val collection = if (fromCaller) "candidates_caller" else "candidates_callee"
        sessions.document(sessionId).collection(collection).add(
            mapOf(
                "sdpMid" to candidate.sdpMid,
                "sdpMLineIndex" to candidate.sdpMLineIndex,
                "sdp" to candidate.sdp
            )
        ).await()
    }

    /** Listens for the *other* side's candidates: pass fromCaller=true to receive the parent's. */
    fun listenIceCandidates(sessionId: String, fromCaller: Boolean): Flow<IceCandidateData> = callbackFlow {
        val collection = if (fromCaller) "candidates_caller" else "candidates_callee"
        val registration = sessions.document(sessionId).collection(collection)
            .addSnapshotListener { snapshot, error ->
                if (error != null) return@addSnapshotListener
                snapshot?.documentChanges?.forEach { change ->
                    if (change.type == com.google.firebase.firestore.DocumentChange.Type.ADDED) {
                        trySend(change.document.toIceCandidate())
                    }
                }
            }
        awaitClose { registration.remove() }
    }

    private fun DocumentSnapshot.toIceCandidate() = IceCandidateData(
        sdpMid = getString("sdpMid"),
        sdpMLineIndex = (getLong("sdpMLineIndex") ?: 0L).toInt(),
        sdp = getString("sdp").orEmpty()
    )
}
