<script setup lang="ts">
const loading = ref(false)
const wallet = ref({ balance: 0 })
const transactions = ref<any[]>([])
</script>

<template>
  <VRow>
    <VCol
      cols="12"
      md="4"
    >
      <VCard title="Wallet">
        <VCardText>
          <h2 class="text-h3 mb-2">
            {{ wallet.balance.toFixed ? wallet.balance.toFixed(2) : wallet.balance }}€
          </h2>
          <VAlert
            type="info"
            variant="tonal"
          >
            Wallet and transaction endpoints are not available in the backend yet.
          </VAlert>
        </VCardText>
      </VCard>
    </VCol>

    <VCol
      cols="12"
      md="8"
    >
      <VCard title="Historique des transactions">
        <VCardText>
          <VSkeletonLoader
            v-if="loading"
            type="table"
          />
          <VTable v-else>
            <thead>
              <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Montant</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!transactions.length">
                <td
                  colspan="4"
                  class="text-medium-emphasis"
                >
                  No transaction history is available yet.
                </td>
              </tr>
              <tr
                v-for="tx in transactions"
                :key="tx.id"
              >
                <td>{{ tx.created_at }}</td>
                <td>{{ tx.type }}</td>
                <td>{{ tx.amount }}</td>
                <td>{{ tx.status }}</td>
              </tr>
            </tbody>
          </VTable>
        </VCardText>
      </VCard>
    </VCol>
  </VRow>
</template>
