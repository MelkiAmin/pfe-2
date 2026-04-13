<script setup lang="ts">
const loading = ref(false)
const withdrawals = ref<any[]>([])
</script>

<template>
  <VCard title="Gestion des retraits organisateurs">
    <VCardText>
      <VSkeletonLoader
        v-if="loading"
        type="table"
      />
      <VAlert
        v-else-if="!withdrawals.length"
        type="info"
        variant="tonal"
      >
        Organizer withdrawal APIs are not available in the backend yet.
      </VAlert>
      <VTable v-else>
        <thead>
          <tr>
            <th>Organisateur</th>
            <th>Montant</th>
            <th>KYC</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="w in withdrawals"
            :key="w.id"
          >
            <td>{{ w.organizer_name }}</td>
            <td>{{ w.amount }}€</td>
            <td>{{ w.kyc_status || 'pending' }}</td>
            <td class="d-flex gap-2">
              <VBtn
                size="small"
                color="success"
                disabled
              >
                Approuver
              </VBtn>
              <VBtn
                size="small"
                variant="tonal"
                color="error"
                disabled
              >
                Rejeter
              </VBtn>
            </td>
          </tr>
        </tbody>
      </VTable>
    </VCardText>
  </VCard>
</template>
