<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">

      <!-- Logo -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-indigo-600">HotelMate</h1>
        <p class="text-gray-500 mt-2">Créer un compte</p>
      </div>

      <!-- Erreur -->
      <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm">
        {{ error }}
      </div>

      <!-- Formulaire -->
      <form @submit.prevent="handleRegister" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Prénom</label>
            <input v-model="form.first_name" type="text" placeholder="Prénom"
              class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nom</label>
            <input v-model="form.last_name" type="text" placeholder="Nom"
              class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nom d'utilisateur</label>
          <input v-model="form.username" type="text" placeholder="username" required
            class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input v-model="form.email" type="email" placeholder="email@exemple.com" required
            class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Téléphone</label>
          <input v-model="form.mobile" type="text" placeholder="+216 XX XXX XXX"
            class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
          <input v-model="form.password" type="password" placeholder="Mot de passe" required
            class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Confirmer mot de passe</label>
          <input v-model="form.password2" type="password" placeholder="Confirmer" required
            class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>

        <button type="submit" :disabled="loading"
          class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-lg transition duration-200 disabled:opacity-50">
          {{ loading ? 'Création...' : "S'inscrire" }}
        </button>
      </form>

      <div class="mt-6 text-center text-sm text-gray-500">
        Déjà un compte ?
        <RouterLink to="/login" class="text-indigo-600 font-medium hover:underline">Se connecter</RouterLink>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

const form = ref({
  first_name: '', last_name: '',
  username: '', email: '',
  mobile: '', password: '', password2: '',
})
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  loading.value = true
  error.value = ''
  try {
    await auth.register(form.value)
    toast.success('Compte créé avec succès !')
    router.push('/dashboard')
  } catch (err: any) {
    const errors = err.response?.data
    if (errors) {
      error.value = Object.values(errors).flat().join(' ')
    } else {
      error.value = 'Une erreur est survenue.'
    }
  } finally {
    loading.value = false
  }
}
</script>