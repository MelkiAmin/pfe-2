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
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50">
          🏠 Tableau de bord
        </RouterLink>
        <RouterLink to="/dashboard/orders"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50">
          🎟️ Mes commandes
        </RouterLink>
        <RouterLink to="/dashboard/profile"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium bg-indigo-50 text-indigo-600">
          👤 Mon profil
        </RouterLink>
        <RouterLink to="/"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50">
          🎭 Événements
        </RouterLink>
        <button @click="handleLogout"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-red-500 hover:bg-red-50">
          🚪 Déconnexion
        </button>
      </nav>
    </aside>

    <!-- Contenu -->
    <main class="ml-64 flex-1 p-8">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-800">Mon profil</h1>
        <p class="text-gray-500 mt-1">Gérez vos informations personnelles</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- Infos profil -->
        <div class="bg-white rounded-2xl shadow-sm p-6">
          <h2 class="font-semibold text-gray-800 mb-4">Informations personnelles</h2>

          <div v-if="success" class="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg mb-4 text-sm">
            ✅ Profil mis à jour avec succès !
          </div>

          <form @submit.prevent="updateProfile" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Prénom</label>
                <input v-model="form.first_name" type="text"
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Nom</label>
                <input v-model="form.last_name" type="text"
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input v-model="form.email" type="email"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Téléphone</label>
              <input v-model="form.mobile" type="text"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Ville</label>
              <input v-model="form.city" type="text"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Adresse</label>
              <textarea v-model="form.address" rows="2"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
            </div>

            <button type="submit" :disabled="loading"
              class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50">
              {{ loading ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </form>
        </div>

        <!-- Changer mot de passe -->
        <div class="bg-white rounded-2xl shadow-sm p-6">
          <h2 class="font-semibold text-gray-800 mb-4">Changer le mot de passe</h2>

          <div v-if="pwSuccess" class="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg mb-4 text-sm">
            ✅ Mot de passe modifié !
          </div>
          <div v-if="pwError" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm">
            {{ pwError }}
          </div>

          <form @submit.prevent="changePassword" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Ancien mot de passe</label>
              <input v-model="pwForm.old_password" type="password"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nouveau mot de passe</label>
              <input v-model="pwForm.new_password" type="password"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Confirmer</label>
              <input v-model="pwForm.new_password2" type="password"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <button type="submit" :disabled="pwLoading"
              class="w-full bg-gray-800 hover:bg-gray-900 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50">
              {{ pwLoading ? 'Modification...' : 'Modifier' }}
            </button>
          </form>
        </div>

      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/axios'

const router = useRouter()
const auth = useAuthStore()

const form = ref({ first_name: '', last_name: '', email: '', mobile: '', city: '', address: '' })
const loading = ref(false)
const success = ref(false)

const pwForm = ref({ old_password: '', new_password: '', new_password2: '' })
const pwLoading = ref(false)
const pwSuccess = ref(false)
const pwError = ref('')

async function fetchProfile() {
  try {
    const response = await api.get('/user/profile/')
    const data = response.data
    form.value = {
      first_name: data.first_name || '',
      last_name: data.last_name || '',
      email: data.email || '',
      mobile: data.mobile || '',
      city: data.city || '',
      address: data.address || '',
    }
  } catch (err) {
    console.error(err)
  }
}

async function updateProfile() {
  loading.value = true
  success.value = false
  try {
    await api.put('/user/profile/', form.value)
    success.value = true
    setTimeout(() => success.value = false, 3000)
  } finally {
    loading.value = false
  }
}

async function changePassword() {
  pwLoading.value = true
  pwError.value = ''
  pwSuccess.value = false
  try {
    await api.post('/user/change-password/', pwForm.value)
    pwSuccess.value = true
    pwForm.value = { old_password: '', new_password: '', new_password2: '' }
    setTimeout(() => pwSuccess.value = false, 3000)
  } catch (err: any) {
    pwError.value = err.response?.data?.error || 'Erreur lors du changement.'
  } finally {
    pwLoading.value = false
  }
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

onMounted(fetchProfile)
</script>