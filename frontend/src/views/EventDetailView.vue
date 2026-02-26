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

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-32">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-indigo-600 border-t-transparent"></div>
    </div>

    <!-- Contenu -->
    <div v-else-if="event" class="max-w-7xl mx-auto px-4 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

        <!-- Colonne gauche -->
        <div class="lg:col-span-2 space-y-6">

          <!-- Image -->
          <div class="rounded-2xl overflow-hidden shadow-sm">
            <img
              :src="event.cover_image || 'https://placehold.co/800x400?text=Event'"
              :alt="event.title"
              class="w-full h-72 object-cover"
            />
          </div>

          <!-- Infos principales -->
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <div class="flex items-start justify-between mb-4">
              <h1 class="text-3xl font-bold text-gray-800">{{ event.title }}</h1>
              <span v-if="event.is_featured" class="bg-yellow-100 text-yellow-700 text-xs font-bold px-3 py-1 rounded-full">
                ⭐ Vedette
              </span>
            </div>

            <div class="grid grid-cols-2 gap-4 mb-6">
              <div class="flex items-center gap-2 text-gray-600">
                <span>📅</span>
                <span class="text-sm">{{ formatDate(event.start_date) }} → {{ formatDate(event.end_date) }}</span>
              </div>
              <div class="flex items-center gap-2 text-gray-600">
                <span>📍</span>
                <span class="text-sm">{{ event.location_address }}</span>
              </div>
              <div class="flex items-center gap-2 text-gray-600">
                <span>🎟️</span>
                <span class="text-sm">{{ event.seats - event.seats_booked }} places restantes / {{ event.seats }}</span>
              </div>
              <div class="flex items-center gap-2 text-gray-600">
                <span>💰</span>
                <span class="text-sm font-semibold text-indigo-600">
                  {{ event.price ? event.price + ' TND' : 'Gratuit' }}
                </span>
              </div>
            </div>

            <div class="border-t pt-4">
              <h2 class="font-semibold text-gray-800 mb-2">Description</h2>
              <p class="text-gray-600 leading-relaxed">{{ event.description }}</p>
            </div>
          </div>

          <!-- Speakers -->
          <div v-if="event.speakers?.length > 0" class="bg-white rounded-2xl shadow-sm p-6">
            <h2 class="font-semibold text-gray-800 mb-4">🎤 Intervenants</h2>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <div v-for="speaker in event.speakers" :key="speaker.id" class="text-center">
                <img
                  :src="speaker.image || 'https://placehold.co/80x80?text=S'"
                  :alt="speaker.name"
                  class="w-16 h-16 rounded-full mx-auto object-cover mb-2"
                />
                <p class="text-sm font-medium text-gray-800">{{ speaker.name }}</p>
                <p class="text-xs text-gray-500">{{ speaker.designation }}</p>
              </div>
            </div>
          </div>

          <!-- Galerie -->
          <div v-if="event.gallery_images?.length > 0" class="bg-white rounded-2xl shadow-sm p-6">
            <h2 class="font-semibold text-gray-800 mb-4">📸 Galerie</h2>
            <div class="grid grid-cols-3 gap-3">
              <img
                v-for="img in event.gallery_images" :key="img.id"
                :src="img.image"
                class="rounded-lg h-28 w-full object-cover hover:opacity-90 cursor-pointer"
              />
            </div>
          </div>

        </div>

        <!-- Colonne droite — Réservation -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-2xl shadow-sm p-6 sticky top-24">
            <h2 class="text-xl font-bold text-gray-800 mb-4">Réserver des billets</h2>

            <div class="bg-indigo-50 rounded-xl p-4 mb-4">
              <p class="text-2xl font-bold text-indigo-600">
                {{ event.price ? event.price + ' TND' : 'Gratuit' }}
              </p>
              <p class="text-sm text-gray-500">par billet</p>
            </div>

            <!-- Quantité -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Nombre de billets</label>
              <div class="flex items-center gap-3">
                <button @click="quantity > 1 && quantity--"
                  class="w-10 h-10 rounded-full border border-gray-300 flex items-center justify-center text-gray-600 hover:bg-gray-50 text-lg">
                  −
                </button>
                <span class="text-xl font-bold text-gray-800 w-8 text-center">{{ quantity }}</span>
                <button @click="quantity < availableSeats && quantity++"
                  class="w-10 h-10 rounded-full border border-gray-300 flex items-center justify-center text-gray-600 hover:bg-gray-50 text-lg">
                  +
                </button>
              </div>
            </div>

            <!-- Total -->
            <div class="border-t border-b py-3 mb-4">
              <div class="flex justify-between text-sm text-gray-600 mb-1">
                <span>{{ quantity }} × {{ event.price }} TND</span>
                <span>{{ (quantity * event.price).toFixed(2) }} TND</span>
              </div>
              <div class="flex justify-between font-bold text-gray-800">
                <span>Total</span>
                <span class="text-indigo-600">{{ (quantity * event.price).toFixed(2) }} TND</span>
              </div>
            </div>

            <!-- Bouton réserver -->
            <button
              @click="handleReservation"
              :disabled="orderLoading || availableSeats === 0"
              class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-xl transition disabled:opacity-50"
            >
              {{ orderLoading ? 'Réservation...' : availableSeats === 0 ? 'Complet' : 'Réserver maintenant' }}
            </button>

            <p class="text-xs text-gray-400 text-center mt-3">
              {{ availableSeats }} places disponibles
            </p>
          </div>
        </div>

      </div>
    </div>

    <!-- Erreur -->
    <div v-else class="text-center py-32 text-gray-400">
      <p class="text-5xl mb-4">😕</p>
      <p class="text-lg">Événement non trouvé</p>
      <RouterLink to="/" class="text-indigo-600 hover:underline mt-2 inline-block">Retour à l'accueil</RouterLink>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/axios'
import { useToast } from 'vue-toastification'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

const event = ref<any>(null)
const loading = ref(false)
const orderLoading = ref(false)
const quantity = ref(1)

const availableSeats = computed(() =>
  event.value ? event.value.seats - event.value.seats_booked : 0
)

async function fetchEvent() {
  loading.value = true
  try {
    const response = await api.get(`/events/${route.params.id}/`)
    event.value = response.data
  } catch {
    event.value = null
  } finally {
    loading.value = false
  }
}

async function handleReservation() {
  if (!auth.isAuthenticated) {
    toast.warning('Veuillez vous connecter pour réserver.')
    router.push('/login')
    return
  }

  orderLoading.value = true
  try {
    const response = await api.post('/orders/', {
      event_id: event.value.id,
      quantity: quantity.value,
    })
    toast.success('Réservation créée avec succès !')
    router.push('/dashboard/orders')
  } catch (err: any) {
    const msg = err.response?.data?.quantity?.[0] || 'Erreur lors de la réservation.'
    toast.error(msg)
  } finally {
    orderLoading.value = false
  }
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'long', year: 'numeric'
  })
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

onMounted(fetchEvent)
</script>