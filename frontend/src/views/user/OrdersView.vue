<template>
  <div class="min-h-screen bg-gray-50 flex">

    <!-- Sidebar -->
    <aside class="w-64 bg-white shadow-sm min-h-screen fixed left-0 top-0 z-40">
      <div class="p-6 border-b">
        <RouterLink to="/" class="text-xl font-bold text-indigo-600">HotelMate</RouterLink>
        <p class="text-xs text-gray-500 mt-1">Dashboard Utilisateur</p>
      </div>
      <nav class="p-4 space-y-1">
        <RouterLink to="/dashboard"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition">
          🏠 Tableau de bord
        </RouterLink>
        <RouterLink to="/dashboard/orders"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium bg-indigo-50 text-indigo-600 transition">
          🎟️ Mes commandes
        </RouterLink>
        <RouterLink to="/dashboard/profile"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition">
          👤 Mon profil
        </RouterLink>
        <RouterLink to="/"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition">
          🎭 Événements
        </RouterLink>
        <button @click="handleLogout"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-red-500 hover:bg-red-50 transition">
          🚪 Déconnexion
        </button>
      </nav>
    </aside>

    <!-- Contenu -->
    <main class="ml-64 flex-1 p-8">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-800">Mes commandes</h1>
        <p class="text-gray-500 mt-1">Historique de vos réservations</p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="space-y-4">
        <div v-for="i in 4" :key="i" class="h-24 bg-white rounded-2xl animate-pulse"></div>
      </div>

      <!-- Liste commandes -->
      <div v-else-if="orders.length > 0" class="space-y-4">
        <div v-for="order in orders" :key="order.id"
          class="bg-white rounded-2xl shadow-sm p-6 flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center text-2xl">🎟️</div>
            <div>
              <p class="font-semibold text-gray-800">Commande #{{ order.id }}</p>
              <p class="text-sm text-gray-500">{{ order.quantity }} billet(s) — {{ formatDate(order.created_at) }}</p>
            </div>
          </div>
          <div class="text-right flex items-center gap-4">
            <div>
              <p class="font-bold text-gray-800">{{ order.total_price }} TND</p>
              <span :class="getStatusClass(order.payment_status)" class="text-xs px-2 py-1 rounded-full">
                {{ getStatusLabel(order.payment_status) }}
              </span>
            </div>
            <button
              v-if="order.payment_status === 0"
              @click="cancelOrder(order.id)"
              class="text-xs text-red-500 border border-red-200 px-3 py-1 rounded-lg hover:bg-red-50">
              Annuler
            </button>
          </div>
        </div>
      </div>

      <!-- Vide -->
      <div v-else class="text-center py-20 text-gray-400">
        <p class="text-5xl mb-4">🎟️</p>
        <p class="text-lg">Aucune commande</p>
        <RouterLink to="/" class="text-indigo-600 hover:underline mt-2 inline-block">
          Découvrir des événements
        </RouterLink>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/axios'
import { useToast } from 'vue-toastification'

const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

const orders = ref([])
const loading = ref(false)

async function fetchOrders() {
  loading.value = true
  try {
    const response = await api.get('/orders/')
    orders.value = response.data
  } finally {
    loading.value = false
  }
}

async function cancelOrder(id: number) {
  try {
    await api.put(`/orders/${id}/cancel/`)
    toast.success('Commande annulée.')
    fetchOrders()
  } catch {
    toast.error('Erreur lors de l\'annulation.')
  }
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'short', year: 'numeric'
  })
}

function getStatusLabel(status: number) {
  const labels: any = { 0: 'En attente', 1: 'Payée', 2: 'Confirmée', 3: 'Annulée' }
  return labels[status] || 'Inconnu'
}

function getStatusClass(status: number) {
  const classes: any = {
    0: 'bg-yellow-100 text-yellow-700',
    1: 'bg-green-100 text-green-700',
    2: 'bg-blue-100 text-blue-700',
    3: 'bg-red-100 text-red-700',
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

onMounted(fetchOrders)
</script>