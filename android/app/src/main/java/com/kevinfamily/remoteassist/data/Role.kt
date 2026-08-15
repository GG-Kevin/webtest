package com.kevinfamily.remoteassist.data

enum class Role {
    PARENT,
    CHILD;

    companion object {
        fun fromStringOrNull(value: String?): Role? =
            entries.firstOrNull { it.name == value }
    }
}
