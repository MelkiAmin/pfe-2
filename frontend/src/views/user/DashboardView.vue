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
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition"
          :class="$route.path === '/dashboard' ? 'bg-indigo-50 text-indigo-600' : 'text-gray-600 hover:bg-gray-50'">
          🏠 Tableau de bord
        </RouterLink>
        <RouterLink to="/dashboard/orders"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition"
          :class="$route.path === '/dashboard/orders' ? 'bg-indigo-50 text-indigo-600' : 'text-gray-600 hover:bg-gray-50'">
          🎟️ Mes commandes
        </RouterLink>
        <RouterLink to="/dashboard/profile"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition"
          :class="$route.path === '/dashboard/profile' ? 'bg-indigo-50 text-indigo-600' : 'text-gray-600 hover:bg-gray-50'">
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

    <!-- Contenu principal -->
    <main class="ml-64 flex-1 p-8">

      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-800">
          Bonjour, {{ auth.user?.first_name || auth.user?.username }} 👋
        </h1>
        <p class="text-gray-500 mt-1">Bienvenue sur votre tableau de bord</p>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-2xl shadow-sm p-6">
          <p class="text-sm text-gray-500">Total commandes</p>
          <p class="text-3xl font-bold text-indigo-600 mt-1">{{ stats.total }}</p>
        </div>
        <div class="bg-white rounded-2xl shadow-sm p-6">
          <p class="text-sm text-gray-500">Commandes payées</p>
          <p class="text-3xl font-bold text-green-600 mt-1">{{ stats.paid }}</p>
        </div>
        <div class="bg-white rounded-2xl shadow-sm p-6">
          <p class="text-sm text-gray-500">En attente</p>
          <p class="text-3xl font-bold text-yellow-600 mt-1">{{ stats.pending }}</p>
        </div>
      </div>

      <!-- Dernières commandes -->
      <div class="bg-white rounded-2xl shadow-sm p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-semibold text-gray-800">Dernières commandes</h2>
          <RouterLink to="/dashboard/orders" class="text-sm text-indigo-600 hover:underline">
            Voir tout →
          </RouterLink>
        </div>

        <div v-if="loadingOrders" class="space-y-3">
          <div v-for="i in 3" :key="i" class="h-16 bg-gray-100 rounded-xl animate-pulse"></div>
        </div>

        <div v-else-if="recentOrders.length > 0" class="space-y-3">
          <div v-for="order in recentOrders" :key="order.id"
            class="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
            <div>
              <p class="font-medium text-gray-800 text-sm">Commande #{{ order.id }}</p>
              <p class="text-xs text-gray-500">{{ formatDate(order.created_at) }}</p>
            </div>
            <div class="text-right">
              <p class="font-semibold text-gray-800">{{ order.total_price }} TND</p>
              <span :class="getStatusClass(order.payment_status)" class="text-xs px-2 py-1 rounded-full">
                {{ getStatusLabel(order.payment_status) }}
              </span>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-8 text-gray-400">
          <p class="text-3xl mb-2">🎟️</p>
          <p class="text-sm">Aucune commande pour le moment</p>
          <RouterLink to="/" class="text-indigo-600 text-sm hover:underline mt-1 inline-block">
            Découvrir des événements
          </RouterLink>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/axios'

const router = useRouter()
const auth = useAuthStore()

const orders = ref([])
const loadingOrders = ref(false)

const recentOrders = computed(() => orders.value.slice(0, 5))
const stats = computed(() => ({
  total: orders.value.length,
  paid: orders.value.filter((o: any) => o.payment_status === 1).length,
  pending: orders.value.filter((o: any) => o.payment_status === 0).length,
}))

async function fetchOrders() {
  loadingOrders.value = true
  try {
    const response = await api.get('/orders/')
    orders.value = response.data
  } catch (err) {
    console.error(err)
  } finally {
    loadingOrders.value = false
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