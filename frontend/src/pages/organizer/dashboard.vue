<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js'
import { apiClient } from '@/services/http/axios'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const range = ref<'day' | 'week' | 'month'>('week')
const loading = ref(true)
const errorMessage = ref('')
const stats = ref({
  total_events: 0,
  published_events: 0,
  total_tickets_sold: 0,
  revenueByEvent: [] as { event: string; revenue: number }[],
  fillRate: 0,
})

const chartData = computed(() => ({
  labels: stats.value.revenueByEvent.map(item => item.event),
  datasets: [{
    label: 'Revenus',
    backgroundColor: 'rgba(25,118,210,0.7)',
    data: stats.value.revenueByEvent.map(item => item.revenue),
  }],
}))

const load = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await apiClient.get('/organizer/dashboard/')
    stats.value = {
      total_events: data.total_events || 0,
      published_events: data.published_events || 0,
      total_tickets_sold: data.total_tickets_sold || 0,
      revenueByEvent: [],
      fillRate: 0,
    }
  }
  catch (error: any) {
    stats.value = {
      total_events: 0,
      published_events: 0,
      total_tickets_sold: 0,
      revenueByEvent: [],
      fillRate: 0,
    }
    errorMessage.value = error?.response?.data?.detail || 'Unable to load organizer dashboard right now.'
  }
  finally {
    loading.value = false
  }
}

watch(range, load)
onMounted(load)
</script>

<template>
  <VRow>
    <VCol cols="12">
      <VCard title="Dashboard organisateur">
        <VCardText class="d-flex gap-4">
          <AppSelect
            v-model="range"
            label="Période"
            :items="[
              { title: 'Jour', value: 'day' },
              { title: 'Semaine', value: 'week' },
              { title: 'Mois', value: 'month' }
            ]"
            style="max-width: 220px;"
            disabled
          />
          <VChip color="primary">
            Events: {{ stats.total_events }}
          </VChip>
          <VChip color="success">
            Published: {{ stats.published_events }}
          </VChip>
          <VChip color="info">
            Tickets sold: {{ stats.total_tickets_sold }}
          </VChip>
        </VCardText>
        <VCardText
          v-if="errorMessage"
          class="pt-0"
        >
          <VAlert
            type="error"
            variant="tonal"
          >
            {{ errorMessage }}
          </VAlert>
        </VCardText>
      </VCard>
    </VCol>

    <VCol cols="12">
      <VCard title="Revenus par événement">
        <VCardText>
          <Bar
            v-if="!loading && stats.revenueByEvent.length"
            :data="chartData"
          />
          <VAlert
            v-else-if="!loading"
            type="info"
            variant="tonal"
          >
            Revenue analytics are not available from the backend yet.
          </VAlert>
          <VSkeletonLoader
            v-else
            type="image"
          />
        </VCardText>
      </VCard>
    </VCol>
  </VRow>
</template>
