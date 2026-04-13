<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const user = computed(() => authStore.user)
</script>

<template>
  <VRow>
    <VCol
      cols="12"
      md="8"
      lg="6"
    >
      <VCard title="Profile">
        <VCardText>
          <p class="text-body-1 mb-3">
            Manage your account details.
          </p>
          <VList lines="one">
            <VListItem
              title="Name"
              :subtitle="user?.full_name || 'N/A'"
            />
            <VListItem
              title="Email"
              :subtitle="user?.email || 'N/A'"
            />
            <VListItem
              title="Role"
              :subtitle="user?.role || 'N/A'"
            />
          </VList>
        </VCardText>
      </VCard>
    </VCol>
  </VRow>
</template>
