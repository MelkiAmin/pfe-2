<template>
  <div class="min-h-screen bg-gray-50">

    <!-- Navbar -->
    <nav class="bg-white shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <RouterLink to="/" class="text-2xl font-bold text-indigo-600">HotelMate</RouterLink>
        <div class="flex items-center gap-4">
          <template v-if="auth.isAuthenticated">
            <RouterLink to="/dashboard" class="text-sm text-gray-600 hover:text-indigo-600">Mon compte</RouterLink>
            <button @click="handleLogout" class="text-sm text-red-500 hover:underline">Déconnexion</button>
          </template>
          <template v-else>
            <RouterLink to="/login" class="text-sm text-gray-600 hover:text-indigo-600">Connexion</RouterLink>
            <RouterLink to="/register" class="bg-indigo-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-indigo-700">
              S'inscrire
            </RouterLink>
          </template>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <div class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-16 px-4">
      <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-4xl font-bold mb-4">Découvrez les meilleurs événements</h1>
        <p class="text-indigo-100 mb-8">Concerts, conférences, festivals et bien plus encore</p>

        <!-- Barre de recherche -->
        <div class="flex gap-2 max-w-2xl mx-auto">
          <input
            v-model="search"
            @input="fetchEvents"
            type="text"
            placeholder="Rechercher un événement..."
            class="flex-1 px-4 py-3 rounded-lg text-gray-800 focus:outline-none"
          />
          <button @click="fetchEvents" class="bg-white text-indigo-600 font-semibold px-6 py-3 rounded-lg hover:bg-indigo-50">
            🔍 Chercher
          </button>
        </div>
      </div>
    </div>

    <!-- Filtres catégories -->
    <div class="max-w-7xl mx-auto px-4 py-6">
      <div class="flex gap-3 overflow-x-auto pb-2">
        <button
          @click="selectedCategory = null; fetchEvents()"
          :class="['px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition',
            !selectedCategory ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 border hover:bg-indigo-50']"
        >
          Tous
        </button>
        <button
          v-for="cat in categories" :key="cat.id"
          @click="selectedCategory = cat.id; fetchEvents()"
          :class="['px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition',
            selectedCategory === cat.id ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 border hover:bg-indigo-50']"
        >
          {{ cat.name }}
        </button>
      </div>
    </div>

    <!-- Liste événements -->
    <div class="max-w-7xl mx-auto px-4 pb-12">

      <!-- Loading -->
      <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 6" :key="i" class="bg-white rounded-xl shadow-sm h-72 animate-pulse">
          <div class="bg-gray-200 h-44 rounded-t-xl"></div>
          <div class="p-4 space-y-2">
            <div class="bg-gray-200 h-4 rounded w-3/4"></div>
            <div class="bg-gray-200 h-3 rounded w-1/2"></div>
          </div>
        </div>
      </div>

      <!-- Événements -->
      <div v-else-if="events.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <RouterLink
          v-for="event in events" :key="event.id"
          :to="`/events/${event.id}`"
          class="bg-white rounded-xl shadow-sm hover:shadow-md transition overflow-hidden group"
        >
          <div class="relative overflow-hidden h-44">
            <img
              :src="event.cover_image || 'https://placehold.co/400x200?text=Event'"
              :alt="event.title"
              class="w-full h-full object-cover group-hover:scale-105 transition duration-300"
            />
            <span v-if="event.is_featured"
              class="absolute top-3 left-3 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded-full">
              ⭐ Vedette
            </span>
            <span class="absolute top-3 right-3 bg-white text-indigo-600 font-bold text-sm px-3 py-1 rounded-full shadow">
              {{ event.price ? event.price + ' TND' : 'Gratuit' }}
            </span>
          </div>
          <div class="p-4">
            <h3 class="font-semibold text-gray-800 text-lg truncate">{{ event.title }}</h3>
            <p class="text-gray-500 text-sm mt-1 truncate">{{ event.location_address }}</p>
            <div class="flex items-center justify-between mt-3">
              <span class="text-indigo-600 text-sm font-medium">📅 {{ formatDate(event.start_date) }}</span>
              <span class="text-gray-400 text-xs">{{ event.seats - event.seats_booked }} places restantes</span>
            </div>
          </div>
        </RouterLink>
      </div>

      <!-- Aucun résultat -->
      <div v-else class="text-center py-20 text-gray-400">
        <p class="text-5xl mb-4">🎭</p>
        <p class="text-lg">Aucun événement trouvé</p>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/axios'

const router = useRouter()
const auth = useAuthStore()

const events = ref([])
const categories = ref([])
const loading = ref(false)
const search = ref('')
const selectedCategory = ref(null)

async function fetchEvents() {
  loading.value = true
  try {
    const params: any = {}
    if (search.value) params.search = search.value
    if (selectedCategory.value) params.category = selectedCategory.value
    const response = await api.get('/events/', { params })
    events.value = response.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    const response = await api.get('/categories/')
    categories.value = response.data
  } catch (err) {
    console.error(err)
  }
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'short', year: 'numeric'
  })
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

onMounted(() => {
  fetchEvents()
  fetchCategories()
})
</script>