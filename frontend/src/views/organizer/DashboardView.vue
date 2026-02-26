<template>
  <div class="min-h-screen bg-gray-50 flex">

    <!-- Sidebar -->
    <aside class="w-64 bg-white shadow-sm min-h-screen fixed left-0 top-0 z-40">
      <div class="p-6 border-b">
        <RouterLink to="/" class="text-xl font-bold text-purple-600">HotelMate</RouterLink>
        <p class="text-xs text-gray-500 mt-1">Espace Organisateur</p>
      </div>
      <nav class="p-4 space-y-1">
        <button @click="activeTab = 'dashboard'"
          :class="['w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition',
            activeTab === 'dashboard' ? 'bg-purple-50 text-purple-600' : 'text-gray-600 hover:bg-gray-50']">
          🏠 Tableau de bord
        </button>
        <button @click="activeTab = 'events'"
          :class="['w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition',
            activeTab === 'events' ? 'bg-purple-50 text-purple-600' : 'text-gray-600 hover:bg-gray-50']">
          🎭 Mes événements
        </button>
        <button @click="activeTab = 'create'"
          :class="['w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition',
            activeTab === 'create' ? 'bg-purple-50 text-purple-600' : 'text-gray-600 hover:bg-gray-50']">
          ➕ Créer événement
        </button>
        <button @click="activeTab = 'withdrawals'"
          :class="['w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition',
            activeTab === 'withdrawals' ? 'bg-purple-50 text-purple-600' : 'text-gray-600 hover:bg-gray-50']">
          💸 Retraits
        </button>
        <button @click="handleLogout"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-red-500 hover:bg-red-50 transition">
          🚪 Déconnexion
        </button>
      </nav>

      <!-- Solde -->
      <div class="p-4 mx-4 mt-4 bg-purple-50 rounded-xl">
        <p class="text-xs text-gray-500">Solde disponible</p>
        <p class="text-xl font-bold text-purple-600">{{ organizer?.balance || 0 }} TND</p>
      </div>
    </aside>

    <!-- Contenu -->
    <main class="ml-64 flex-1 p-8">

      <!-- Dashboard Tab -->
      <div v-if="activeTab === 'dashboard'">
        <div class="mb-6">
          <h1 class="text-2xl font-bold text-gray-800">Bonjour, {{ organizer?.firstname || organizer?.username }} 👋</h1>
          <p class="text-gray-500">Tableau de bord organisateur</p>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div class="bg-white rounded-2xl shadow-sm p-5">
            <p class="text-xs text-gray-500">Événements</p>
            <p class="text-3xl font-bold text-purple-600 mt-1">{{ stats.total_events || 0 }}</p>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-5">
            <p class="text-xs text-gray-500">Commandes</p>
            <p class="text-3xl font-bold text-blue-600 mt-1">{{ stats.total_orders || 0 }}</p>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-5">
            <p class="text-xs text-gray-500">Commandes payées</p>
            <p class="text-3xl font-bold text-green-600 mt-1">{{ stats.paid_orders || 0 }}</p>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-5">
            <p class="text-xs text-gray-500">Revenus totaux</p>
            <p class="text-3xl font-bold text-yellow-600 mt-1">{{ stats.total_revenue || 0 }} TND</p>
          </div>
        </div>

        <!-- Événements récents -->
        <div class="bg-white rounded-2xl shadow-sm p-6">
          <h2 class="font-semibold text-gray-800 mb-4">Mes événements récents</h2>
          <div v-if="events.length > 0" class="space-y-3">
            <div v-for="event in events.slice(0,5)" :key="event.id"
              class="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
              <div>
                <p class="font-medium text-gray-800">{{ event.title }}</p>
                <p class="text-xs text-gray-500">{{ formatDate(event.start_date) }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-purple-600">{{ event.price }} TND</p>
                <span :class="event.status ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                  class="text-xs px-2 py-1 rounded-full">
                  {{ event.status ? 'Actif' : 'En attente' }}
                </span>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-400">
            <p>Aucun événement créé</p>
            <button @click="activeTab = 'create'" class="text-purple-600 text-sm hover:underline mt-1">
              Créer votre premier événement
            </button>
          </div>
        </div>
      </div>

      <!-- Events Tab -->
      <div v-if="activeTab === 'events'">
        <div class="mb-6 flex items-center justify-between">
          <h1 class="text-2xl font-bold text-gray-800">Mes événements</h1>
          <button @click="activeTab = 'create'"
            class="bg-purple-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-purple-700">
            ➕ Créer un événement
          </button>
        </div>

        <div v-if="events.length > 0" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div v-for="event in events" :key="event.id"
            class="bg-white rounded-2xl shadow-sm overflow-hidden">
            <img :src="event.cover_image || 'https://placehold.co/400x150?text=Event'"
              class="w-full h-36 object-cover" />
            <div class="p-4">
              <h3 class="font-semibold text-gray-800">{{ event.title }}</h3>
              <p class="text-sm text-gray-500 mt-1">📅 {{ formatDate(event.start_date) }}</p>
              <div class="flex items-center justify-between mt-3">
                <span class="font-bold text-purple-600">{{ event.price }} TND</span>
                <span :class="event.status ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                  class="text-xs px-2 py-1 rounded-full">
                  {{ event.status ? 'Actif' : 'En attente' }}
                </span>
              </div>
              <div class="mt-3 text-xs text-gray-400">
                {{ event.seats_booked }}/{{ event.seats }} places réservées
              </div>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-20 text-gray-400">
          <p class="text-5xl mb-4">🎭</p>
          <p>Aucun événement créé</p>
        </div>
      </div>

      <!-- Create Event Tab -->
      <div v-if="activeTab === 'create'">
        <div class="mb-6">
          <h1 class="text-2xl font-bold text-gray-800">Créer un événement</h1>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-6 max-w-2xl">
          <div v-if="createSuccess" class="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg mb-4 text-sm">
            ✅ Événement créé avec succès !
          </div>
          <div v-if="createError" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm">
            {{ createError }}
          </div>

          <form @submit.prevent="createEvent" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Titre *</label>
              <input v-model="eventForm.title" type="text" required
                class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Date début *</label>
                <input v-model="eventForm.start_date" type="date" required
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Date fin *</label>
                <input v-model="eventForm.end_date" type="date" required
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Prix (TND) *</label>
                <input v-model="eventForm.price" type="number" min="0" required
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Nombre de places *</label>
                <input v-model="eventForm.seats" type="number" min="1" required
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Adresse *</label>
              <input v-model="eventForm.location_address" type="text" required
                class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description courte *</label>
              <input v-model="eventForm.short_description" type="text" required
                class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description complète *</label>
              <textarea v-model="eventForm.description" rows="4" required
                class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Image de couverture (URL)</label>
              <input v-model="eventForm.cover_image" type="text"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" />
            </div>

            <button type="submit" :disabled="createLoading"
              class="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50">
              {{ createLoading ? 'Création...' : 'Créer l\'événement' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Withdrawals Tab -->
      <div v-if="activeTab === 'withdrawals'">
        <div class="mb-6">
          <h1 class="text-2xl font-bold text-gray-800">Retraits</h1>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Demande retrait -->
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <h2 class="font-semibold text-gray-800 mb-4">Demander un retrait</h2>
            <div class="bg-purple-50 rounded-xl p-4 mb-4">
              <p class="text-sm text-gray-500">Solde disponible</p>
              <p class="text-2xl font-bold text-purple-600">{{ organizer?.balance || 0 }} TND</p>
            </div>

            <div v-if="withdrawError" class="bg-red-50 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm">{{ withdrawError }}</div>
            <div v-if="withdrawSuccess" class="bg-green-50 text-green-600 px-4 py-3 rounded-lg mb-4 text-sm">✅ Demande envoyée !</div>

            <form @submit.prevent="requestWithdraw" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Méthode</label>
                <select v-model="withdrawForm.method_id"
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500">
                  <option v-for="m in withdrawMethods" :key="m.id" :value="m.id">
                    {{ m.name }} ({{ m.currency }})
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Montant (TND)</label>
                <input v-model="withdrawForm.amount" type="number" min="0"
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" />
              </div>
              <button type="submit" :disabled="withdrawLoading"
                class="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50">
                {{ withdrawLoading ? 'Envoi...' : 'Demander le retrait' }}
              </button>
            </form>
          </div>

          <!-- Historique retraits -->
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <h2 class="font-semibold text-gray-800 mb-4">Historique retraits</h2>
            <div v-if="withdrawals.length > 0" class="space-y-3">
              <div v-for="w in withdrawals" :key="w.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                <div>
                  <p class="text-sm font-medium text-gray-800">{{ w.amount }} TND</p>
                  <p class="text-xs text-gray-500">{{ formatDate(w.created_at) }}</p>
                </div>
                <span :class="{
                  'bg-green-100 text-green-700': w.status === 1,
                  'bg-yellow-100 text-yellow-700': w.status === 2,
                  'bg-red-100 text-red-700': w.status === 3,
                }" class="text-xs px-2 py-1 rounded-full">
                  {{ w.status === 1 ? 'Approuvé' : w.status === 2 ? 'En attente' : 'Rejeté' }}
                </span>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-400 text-sm">Aucun retrait</div>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useOrganizerStore } from '@/stores/organizer'
import organizerApi from '@/api/organizerAxios'
import { useToast } from 'vue-toastification'

const router = useRouter()
const orgStore = useOrganizerStore()
const toast = useToast()

const organizer = ref(orgStore.organizer)
const activeTab = ref('dashboard')

const stats = ref({})
const events = ref([])
const withdrawals = ref([])
const withdrawMethods = ref([])

// Create event
const eventForm = ref({
  title: '', start_date: '', end_date: '',
  price: 0, seats: 0, location_address: '',
  short_description: '', description: '', cover_image: '',
})
const createLoading = ref(false)
const createSuccess = ref(false)
const createError = ref('')

// Withdraw
const withdrawForm = ref({ method_id: '', amount: 0 })
const withdrawLoading = ref(false)
const withdrawSuccess = ref(false)
const withdrawError = ref('')

async function fetchStats() {
  try {
    const response = await organizerApi.get('/organizer/stats/')
    stats.value = response.data
  } catch {}
}

async function fetchEvents() {
  try {
    const response = await organizerApi.get('/organizer/events/')
    events.value = response.data
  } catch {}
}

async function fetchWithdrawals() {
  try {
    const response = await organizerApi.get('/organizer/withdrawals/')
    withdrawals.value = response.data
  } catch {}
}

async function fetchWithdrawMethods() {
  try {
    const response = await organizerApi.get('/organizer/withdraw-methods/')
    withdrawMethods.value = response.data
  } catch {}
}

async function createEvent() {
  createLoading.value = true
  createError.value = ''
  createSuccess.value = false
  try {
    await organizerApi.post('/events/', eventForm.value)
    createSuccess.value = true
    fetchEvents()
    setTimeout(() => {
      createSuccess.value = false
      activeTab.value = 'events'
    }, 2000)
  } catch (err: any) {
    createError.value = Object.values(err.response?.data || {}).flat().join(' ')
  } finally {
    createLoading.value = false
  }
}

async function requestWithdraw() {
  withdrawLoading.value = true
  withdrawError.value = ''
  withdrawSuccess.value = false
  try {
    await organizerApi.post('/organizer/withdrawals/', withdrawForm.value)
    withdrawSuccess.value = true
    fetchWithdrawals()
  } catch (err: any) {
    withdrawError.value = err.response?.data?.error || 'Erreur lors de la demande.'
  } finally {
    withdrawLoading.value = false
  }
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'short', year: 'numeric'
  })
}

function handleLogout() {
  orgStore.logout()
  router.push('/organizer/login')
}

onMounted(() => {
  if (!orgStore.isAuthenticated) {
    router.push('/organizer/login')
    return
  }
  fetchStats()
  fetchEvents()
  fetchWithdrawals()
  fetchWithdrawMethods()
})
</script>