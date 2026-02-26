<template>
  <div class="min-h-screen bg-gray-100 flex">

    <!-- Sidebar -->
    <aside class="w-64 bg-gray-900 text-white min-h-screen fixed left-0 top-0 z-40">
      <div class="p-6 border-b border-gray-700">
        <h1 class="text-xl font-bold text-white">HotelMate</h1>
        <p class="text-xs text-gray-400 mt-1">Panneau d'administration</p>
      </div>
      <nav class="p-4 space-y-1">
        <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
          :class="['w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition',
            activeTab === tab.key ? 'bg-white text-gray-900' : 'text-gray-300 hover:bg-gray-800']">
          {{ tab.icon }} {{ tab.label }}
        </button>
        <button @click="handleLogout"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-red-400 hover:bg-gray-800 transition">
          🚪 Déconnexion
        </button>
      </nav>
    </aside>

    <!-- Contenu -->
    <main class="ml-64 flex-1 p-8">

      <!-- ── Stats Tab ───────────────────────────────────────── -->
      <div v-if="activeTab === 'stats'">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Tableau de bord</h1>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="bg-white rounded-2xl shadow-sm p-5">
            <p class="text-xs text-gray-500">Utilisateurs</p>
            <p class="text-3xl font-bold text-blue-600 mt-1">{{ stats.total_users || 0 }}</p>
            <p class="text-xs text-green-500 mt-1">{{ stats.active_users || 0 }} actifs</p>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-5">
            <p class="text-xs text-gray-500">Organisateurs</p>
            <p class="text-3xl font-bold text-purple-600 mt-1">{{ stats.total_organizers || 0 }}</p>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-5">
            <p class="text-xs text-gray-500">Événements</p>
            <p class="text-3xl font-bold text-indigo-600 mt-1">{{ stats.total_events || 0 }}</p>
            <p class="text-xs text-yellow-500 mt-1">{{ stats.pending_events || 0 }} en attente</p>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-5">
            <p class="text-xs text-gray-500">Revenus</p>
            <p class="text-3xl font-bold text-green-600 mt-1">{{ stats.total_revenue || 0 }}</p>
            <p class="text-xs text-gray-400 mt-1">TND</p>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="bg-white rounded-2xl shadow-sm p-5">
            <p class="text-xs text-gray-500">Total commandes</p>
            <p class="text-3xl font-bold text-gray-800 mt-1">{{ stats.total_orders || 0 }}</p>
            <p class="text-xs text-green-500 mt-1">{{ stats.paid_orders || 0 }} payées</p>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-5">
            <p class="text-xs text-gray-500">Retraits en attente</p>
            <p class="text-3xl font-bold text-orange-600 mt-1">{{ stats.pending_withdrawals || 0 }}</p>
          </div>
        </div>
      </div>

      <!-- ── Users Tab ───────────────────────────────────────── -->
      <div v-if="activeTab === 'users'">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Gestion des utilisateurs</h1>
        <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr>
                <th class="px-6 py-4 text-left">Utilisateur</th>
                <th class="px-6 py-4 text-left">Email</th>
                <th class="px-6 py-4 text-left">Statut</th>
                <th class="px-6 py-4 text-left">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
                <td class="px-6 py-4">
                  <p class="font-medium text-gray-800">{{ user.username }}</p>
                  <p class="text-xs text-gray-400">{{ user.first_name }} {{ user.last_name }}</p>
                </td>
                <td class="px-6 py-4 text-gray-600">{{ user.email }}</td>
                <td class="px-6 py-4">
                  <span :class="user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
                    class="text-xs px-2 py-1 rounded-full">
                    {{ user.is_active ? 'Actif' : 'Banni' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <button @click="banUser(user.id)"
                    :class="user.is_active ? 'text-red-500 hover:text-red-700' : 'text-green-500 hover:text-green-700'"
                    class="text-xs font-medium">
                    {{ user.is_active ? 'Bannir' : 'Réactiver' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ── Events Tab ──────────────────────────────────────── -->
      <div v-if="activeTab === 'events'">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Gestion des événements</h1>
        <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr>
                <th class="px-6 py-4 text-left">Événement</th>
                <th class="px-6 py-4 text-left">Prix</th>
                <th class="px-6 py-4 text-left">Statut</th>
                <th class="px-6 py-4 text-left">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="event in events" :key="event.id" class="hover:bg-gray-50">
                <td class="px-6 py-4">
                  <p class="font-medium text-gray-800">{{ event.title }}</p>
                  <p class="text-xs text-gray-400">{{ formatDate(event.start_date) }}</p>
                </td>
                <td class="px-6 py-4 text-gray-600">{{ event.price }} TND</td>
                <td class="px-6 py-4">
                  <span :class="event.status ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                    class="text-xs px-2 py-1 rounded-full">
                    {{ event.status ? 'Actif' : 'En attente' }}
                  </span>
                </td>
                <td class="px-6 py-4 flex gap-2">
                  <button @click="verifyEvent(event.id, 'approve')"
                    class="text-xs text-green-600 border border-green-200 px-2 py-1 rounded hover:bg-green-50">
                    ✅ Approuver
                  </button>
                  <button @click="verifyEvent(event.id, 'reject')"
                    class="text-xs text-red-600 border border-red-200 px-2 py-1 rounded hover:bg-red-50">
                    ❌ Rejeter
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ── Orders Tab ──────────────────────────────────────── -->
      <div v-if="activeTab === 'orders'">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Toutes les commandes</h1>
        <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr>
                <th class="px-6 py-4 text-left">ID</th>
                <th class="px-6 py-4 text-left">Événement</th>
                <th class="px-6 py-4 text-left">Quantité</th>
                <th class="px-6 py-4 text-left">Total</th>
                <th class="px-6 py-4 text-left">Statut</th>
                <th class="px-6 py-4 text-left">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="order in orders" :key="order.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 font-medium">#{{ order.id }}</td>
                <td class="px-6 py-4 text-gray-600">Event #{{ order.event_id }}</td>
                <td class="px-6 py-4 text-gray-600">{{ order.quantity }}</td>
                <td class="px-6 py-4 font-semibold text-gray-800">{{ order.total_price }} TND</td>
                <td class="px-6 py-4">
                  <span :class="{
                    'bg-yellow-100 text-yellow-700': order.payment_status === 0,
                    'bg-green-100 text-green-700': order.payment_status === 1,
                    'bg-red-100 text-red-700': order.payment_status === 3,
                  }" class="text-xs px-2 py-1 rounded-full">
                    {{ order.payment_status === 0 ? 'En attente' : order.payment_status === 1 ? 'Payée' : 'Annulée' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-gray-400 text-xs">{{ formatDate(order.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ── Withdrawals Tab ─────────────────────────────────── -->
      <div v-if="activeTab === 'withdrawals'">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Gestion des retraits</h1>
        <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr>
                <th class="px-6 py-4 text-left">ID</th>
                <th class="px-6 py-4 text-left">Montant</th>
                <th class="px-6 py-4 text-left">Devise</th>
                <th class="px-6 py-4 text-left">Statut</th>
                <th class="px-6 py-4 text-left">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="w in withdrawals" :key="w.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 font-medium">#{{ w.id }}</td>
                <td class="px-6 py-4 font-semibold text-gray-800">{{ w.amount }}</td>
                <td class="px-6 py-4 text-gray-600">{{ w.currency }}</td>
                <td class="px-6 py-4">
                  <span :class="{
                    'bg-green-100 text-green-700': w.status === 1,
                    'bg-yellow-100 text-yellow-700': w.status === 2,
                    'bg-red-100 text-red-700': w.status === 3,
                  }" class="text-xs px-2 py-1 rounded-full">
                    {{ w.status === 1 ? 'Approuvé' : w.status === 2 ? 'En attente' : 'Rejeté' }}
                  </span>
                </td>
                <td class="px-6 py-4 flex gap-2">
                  <button v-if="w.status === 2" @click="processWithdrawal(w.id, 'approve')"
                    class="text-xs text-green-600 border border-green-200 px-2 py-1 rounded hover:bg-green-50">
                    ✅ Approuver
                  </button>
                  <button v-if="w.status === 2" @click="processWithdrawal(w.id, 'reject')"
                    class="text-xs text-red-600 border border-red-200 px-2 py-1 rounded hover:bg-red-50">
                    ❌ Rejeter
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ── Support Tab ─────────────────────────────────────── -->
      <div v-if="activeTab === 'support'">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Tickets de support</h1>
        <div class="space-y-4">
          <div v-for="ticket in tickets" :key="ticket.id"
            class="bg-white rounded-2xl shadow-sm p-5 flex items-center justify-between">
            <div>
              <p class="font-semibold text-gray-800">{{ ticket.subject }}</p>
              <p class="text-xs text-gray-500 mt-1">
                Ticket #{{ ticket.ticket }} — {{ ticket.name }} — {{ formatDate(ticket.created_at) }}
              </p>
            </div>
            <div class="flex items-center gap-3">
              <span :class="{
                'bg-green-100 text-green-700': ticket.status === 0,
                'bg-blue-100 text-blue-700': ticket.status === 1,
                'bg-yellow-100 text-yellow-700': ticket.status === 2,
                'bg-gray-100 text-gray-700': ticket.status === 3,
              }" class="text-xs px-2 py-1 rounded-full">
                {{ ['Ouvert', 'Répondu', 'En attente', 'Fermé'][ticket.status] }}
              </span>
              <span :class="{
                'bg-gray-100 text-gray-600': ticket.priority === 1,
                'bg-yellow-100 text-yellow-700': ticket.priority === 2,
                'bg-red-100 text-red-700': ticket.priority === 3,
              }" class="text-xs px-2 py-1 rounded-full">
                {{ ['', 'Bas', 'Moyen', 'Urgent'][ticket.priority] }}
              </span>
            </div>
          </div>
          <div v-if="tickets.length === 0" class="text-center py-12 text-gray-400">
            Aucun ticket de support
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import adminApi from '@/api/adminAxios'
import { useToast } from 'vue-toastification'

const router = useRouter()
const toast = useToast()

const activeTab = ref('stats')
const tabs = [
  { key: 'stats', icon: '📊', label: 'Statistiques' },
  { key: 'users', icon: '👥', label: 'Utilisateurs' },
  { key: 'events', icon: '🎭', label: 'Événements' },
  { key: 'orders', icon: '🎟️', label: 'Commandes' },
  { key: 'withdrawals', icon: '💸', label: 'Retraits' },
  { key: 'support', icon: '🎧', label: 'Support' },
]

const stats = ref({})
const users = ref([])
const events = ref([])
const orders = ref([])
const withdrawals = ref([])
const tickets = ref([])

async function fetchAll() {
  try {
    const [s, u, e, o, w, t] = await Promise.all([
      adminApi.get('/admin/stats/'),
      adminApi.get('/admin/users/'),
      adminApi.get('/admin/events/'),
      adminApi.get('/admin/orders/'),
      adminApi.get('/admin/withdrawals/'),
      adminApi.get('/admin/support/'),
    ])
    stats.value = s.data
    users.value = u.data
    events.value = e.data
    orders.value = o.data
    withdrawals.value = w.data
    tickets.value = t.data
  } catch (err) {
    console.error(err)
  }
}

async function banUser(id: number) {
  try {
    await adminApi.put(`/admin/users/${id}/ban/`)
    toast.success('Statut utilisateur modifié.')
    fetchAll()
  } catch {
    toast.error('Erreur.')
  }
}

async function verifyEvent(id: number, action: string) {
  try {
    await adminApi.put(`/admin/events/${id}/verify/`, { action })
    toast.success(action === 'approve' ? 'Événement approuvé.' : 'Événement rejeté.')
    fetchAll()
  } catch {
    toast.error('Erreur.')
  }
}

async function processWithdrawal(id: number, action: string) {
  try {
    await adminApi.put(`/admin/withdrawals/${id}/process/`, { action })
    toast.success(action === 'approve' ? 'Retrait approuvé.' : 'Retrait rejeté.')
    fetchAll()
  } catch {
    toast.error('Erreur.')
  }
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'short', year: 'numeric'
  })
}

function handleLogout() {
  localStorage.removeItem('admin_access_token')
  localStorage.removeItem('admin')
  router.push('/admin/login')
}

onMounted(() => {
  if (!localStorage.getItem('admin_access_token')) {
    router.push('/admin/login')
    return
  }
  fetchAll()
})
</script>