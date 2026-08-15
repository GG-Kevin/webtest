package com.kevinfamily.remoteassist.data

import com.google.firebase.firestore.FieldValue
import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.tasks.await
import java.util.concurrent.TimeUnit
import kotlin.random.Random

/**
 * One-time pairing between a parent device and a child device via a short
 * numeric code, stored in Firestore under `pairings/{code}`. Firestore is
 * the only backend piece this app uses — no custom server, no Cloud Functions.
 */
class PairingRepository(
    private val db: FirebaseFirestore = FirebaseFirestore.getInstance()
) {
    private val pairings get() = db.collection("pairings")
    private val devices get() = db.collection("devices")

    private val codeTtlMillis = TimeUnit.MINUTES.toMillis(10)

    /** Parent side: create a fresh 6-digit code and the pairing doc that awaits a child. */
    suspend fun createPairingCode(parentDeviceId: String): String {
        val code = (100000 + Random.nextInt(900000)).toString()
        val doc = mapOf(
            "parentDeviceId" to parentDeviceId,
            "childDeviceId" to null,
            "createdAt" to FieldValue.serverTimestamp(),
            "expiresAtMillis" to (System.currentTimeMillis() + codeTtlMillis)
        )
        pairings.document(code).set(doc).await()
        return code
    }

    /** Parent side: listen for a child to claim this code. Emits the child's device id once. */
    fun awaitChildJoin(code: String): Flow<String> = callbackFlow {
        val registration = pairings.document(code).addSnapshotListener { snapshot, error ->
            if (error != null) return@addSnapshotListener
            val childId = snapshot?.getString("childDeviceId")
            if (childId != null) trySend(childId)
        }
        awaitClose { registration.remove() }
    }

    /**
     * Child side: claim a pairing code. Returns the parent's device id on success,
     * or null if the code is missing, expired, or already claimed.
     */
    suspend fun claimPairingCode(code: String, childDeviceId: String): String? {
        val docRef = pairings.document(code)
        return db.runTransaction { tx ->
            val snapshot = tx.get(docRef)
            if (!snapshot.exists()) return@runTransaction null
            val expiresAt = snapshot.getLong("expiresAtMillis") ?: 0L
            if (System.currentTimeMillis() > expiresAt) return@runTransaction null
            if (snapshot.getString("childDeviceId") != null) return@runTransaction null
            val parentId = snapshot.getString("parentDeviceId") ?: return@runTransaction null
            tx.update(docRef, "childDeviceId", childDeviceId)
            parentId
        }.await()
    }

    /** Records this device's role and paired partner so either side can look the other up. */
    suspend fun saveDeviceRecord(deviceId: String, role: Role, partnerId: String, displayName: String) {
        devices.document(deviceId).set(
            mapOf(
                "role" to role.name,
                "partnerId" to partnerId,
                "displayName" to displayName,
                "updatedAt" to FieldValue.serverTimestamp()
            )
        ).await()
    }
}
