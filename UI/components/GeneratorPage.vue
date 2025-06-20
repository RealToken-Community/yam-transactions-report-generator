<template>
  <v-app>
    <v-main>
      <v-container fluid class="pa-0">
        <v-row no-gutters>
          <v-col cols="12">
            <!-- Main hero section with gradient background -->
            <div class="hero-section">
              <v-container>
                <v-row justify="center" align="center" class="min-vh-100">
                  <v-col cols="12" md="6" lg="5">
                    <!-- Main form card with glass effect -->
                    <v-card class="mx-auto glass-card" elevation="0" rounded="xl">
                      <v-card-text class="pa-8">
                        
                        <!-- Header section -->
                        <div class="text-center mb-8">
                          <h1 class="text-h5 font-weight-bold gradient-text mb-4">
                            YAM transactions PDF Generator
                          </h1>
                          <p class="text-subtitle-1 text-medium-emphasis">
                            Generate a PDF report of all your YAM transactions
                          </p>
                        </div>

                        <v-form @submit.prevent="handleSubmit">
                          
                          <!-- Wallet address input section -->
                          <div class="mb-3">
                            <div class="d-flex align-center mb-3" style="gap: 0px;">
                              <v-text-field
                                v-model="textInput"
                                label="Add your wallet address"
                                placeholder="Add one or more wallet addresses"
                                variant="outlined"
                                color="#8b6914"
                                prepend-inner-icon="mdi-wallet-outline"
                                hide-details
                                class="flex-grow-1"
                                density="compact"
                                :error="addressInputError"
                                @keydown.enter.prevent="addWalletAddress"
                                @input="addressInputError = false"
                              />
                              <v-btn
                                @click="addWalletAddress"
                                :disabled="!textInput.trim()"
                                size="large"
                                icon
                                variant="text"
                                style="color: #8b6914; min-width: auto; padding: 4px;"
                              >
                                <v-icon icon="mdi-plus-circle" size="large" />
                              </v-btn>
                            </div>
                            
                            <!-- Address validation error -->
                            <v-alert
                              v-if="addressInputError"
                              variant="text"
                              density="compact"
                              class="mt-1"
                              color="error"
                            >
                              Invalid address
                            </v-alert>
                            
                            <!-- Display added wallet addresses as chips -->
                            <v-card
                              v-if="walletAddresses.length > 0"
                              class="pa-3"
                              variant="outlined"
                              rounded="lg"
                              style="border-color: #8b6914; min-height: 60px;"
                            >
                              <div class="d-flex flex-wrap" style="gap: 8px 8px;">
                                <v-chip
                                  v-for="(address, index) in walletAddresses"
                                  :key="index"
                                  closable
                                  @click:close="removeWalletAddress(index)"
                                  color="#8b6914"
                                  variant="elevated"
                                  size="small"
                                >
                                  {{ address }}
                                </v-chip>
                              </div>
                            </v-card>
                          </div>

                          <!-- Date selection section -->
                          <v-card 
                            class="switch-card mb-6" 
                            :class="{ 'switch-card-error': dateSelectionError }"
                            variant="outlined" 
                            rounded="lg"
                          >
                            <v-card-text class="pa-4">
                              <h4 class="text-subtitle-1 mb-3 text-center font-weight-bold">Date selection</h4>
                              <v-row>
                                <v-col cols="12" sm="6">
                                  <v-text-field
                                    v-model="startDate"
                                    label="Start date"
                                    type="date"
                                    variant="outlined"
                                    color="#8b6914"
                                    hide-details
                                    density="compact"
                                  />
                                </v-col>
                                <v-col cols="12" sm="6">
                                  <v-text-field
                                    v-model="endDate"
                                    label="End date"
                                    type="date"
                                    variant="outlined"
                                    color="#8b6914"
                                    hide-details
                                    density="compact"
                                  />
                                </v-col>
                              </v-row>
                              
                              <!-- Date validation error messages -->
                              <v-alert
                                v-if="dateSelectionError"
                                variant="text"
                                density="compact"
                                class="mt-3"
                                color="error"
                              >
                                {{ dateErrorMessage }}
                              </v-alert>
                            </v-card-text>
                          </v-card>

                          <!-- Configuration options: Transaction types and additional columns -->
                          <v-row class="mb-8">
                            
                            <!-- Transaction type selection (Buy/Sell/Exchange) -->
                            <v-col cols="12" sm="6">
                              <v-card 
                                class="switch-card" 
                                :class="{ 'switch-card-error': transactionTypesError }"
                                variant="outlined" 
                                rounded="lg"
                              >
                                <v-card-text class="text-center pa-4">
                                  <h4 class="text-subtitle-1 mb-3 font-weight-bold">Transactions type</h4>
                                  <div class="d-flex align-center justify-start switch-row">
                                    <v-switch
                                      v-model="transactionTypes"
                                      color="#8b6914"
                                      value="Buy"
                                      hide-details
                                      inset
                                    />
                                    <span class="text-subtitle-1 ml-3">Buy</span>
                                  </div>
                                  <div class="d-flex align-center justify-start switch-row">
                                    <v-switch
                                      v-model="transactionTypes"
                                      color="#8b6914"
                                      value="Sell"
                                      hide-details
                                      inset
                                    />
                                    <span class="text-subtitle-1 ml-3">Sell</span>
                                  </div>
                                  <div class="d-flex align-center justify-start switch-row">
                                    <v-switch
                                      v-model="transactionTypes"
                                      color="#8b6914"
                                      value="Exchange"
                                      hide-details
                                      inset
                                    />
                                    <span class="text-subtitle-1 ml-3">Exchange</span>
                                  </div>
                                  
                                  <!-- Transaction type validation error -->
                                  <v-alert
                                    v-if="transactionTypesError"
                                    variant="text"
                                    density="compact"
                                    class="mt-3"
                                    color="error"
                                  >
                                    Select one transaction type
                                  </v-alert>
                                </v-card-text>
                              </v-card>
                            </v-col>
                            
                            <!-- Additional column options -->
                            <v-col cols="12" sm="6">
                              <v-card class="switch-card" variant="outlined" rounded="lg">
                                <v-card-text class="text-center pa-4">
                                  <h4 class="text-subtitle-1 mb-3 font-weight-bold">Additional column</h4>
                                  <div class="d-flex align-center justify-start switch-row">
                                    <v-switch
                                      v-model="includeTxUrl"
                                      color="#8b6914"
                                      hide-details
                                      inset
                                    />
                                    <span class="text-subtitle-1 ml-3">Tx url</span>
                                    <v-tooltip text="Display a column with a link to the related transaction in gnosisscan">
                                      <template v-slot:activator="{ props }">
                                        <v-icon 
                                          v-bind="props"
                                          icon="mdi-information-outline"
                                          size="small"
                                          color="#8b6914"
                                          class="ml-2"
                                        />
                                      </template>
                                    </v-tooltip>
                                  </div>
                                </v-card-text>
                              </v-card>
                            </v-col>
                          </v-row>

                          <!-- Submit button -->
                          <div class="text-center">
                            <v-btn
                              type="submit"
                              size="large"
                              rounded="pill"
                              class="action-btn px-8"
                              :loading="loading"
                            >
                              <v-icon start icon="mdi-download" />
                              Download PDF
                            </v-btn>
                          </div>
                        </v-form>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-container>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <!-- Global notification snackbar -->
    <v-snackbar
      v-model="snackbar"
      :color="snackbarColor"
      timeout="5000"
      rounded="pill"
    >
      {{ snackbarText }}
    </v-snackbar>
  </v-app>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'ModernConfigPage',
  setup() {
    // ===== REACTIVE DATA =====
    
    // Form input fields
    const textInput = ref('')
    const walletAddresses = ref([])
    const startDate = ref('')
    const endDate = ref('')
    const transactionTypes = ref(['Buy', 'Sell'])
    const includeTxUrl = ref(true)
    
    // UI state management
    const loading = ref(false)
    const snackbar = ref(false)
    const snackbarText = ref('')
    const snackbarColor = ref('success')
    
    // Error handling
    const addressInputError = ref(false)
    const dateValidationTriggered = ref(false)

    // ===== COMPUTED PROPERTIES FOR VALIDATION =====
    
    // Check if at least one transaction type is selected
    const transactionTypesError = computed(() => {
      return transactionTypes.value.length === 0
    })

    // Date validation logic
    const dateSelectionError = computed(() => {
      if (!dateValidationTriggered.value) return false
      
      if (!startDate.value || !endDate.value) {
        return true
      }
      
      if (new Date(startDate.value) > new Date(endDate.value)) {
        return true
      }
      
      return false
    })
    
    // Dynamic error messages for date validation
    const dateErrorMessage = computed(() => {
      if (!dateValidationTriggered.value) return ''
      
      if (!startDate.value || !endDate.value) {
        return 'Select the dates to generate your PDF report'
      }
      
      if (new Date(startDate.value) > new Date(endDate.value)) {
        return 'Start date must be before end date'
      }
      
      return ''
    })

    // ===== DATA FORMATTING FOR API =====
    
    // Format dates with proper time boundaries for API
    const formattedStartDate = computed(() => {
      return startDate.value ? `${startDate.value}T00:00:00` : ''
    })

    const formattedEndDate = computed(() => {
      return endDate.value ? `${endDate.value}T23:59:59` : ''
    })

    // Prepare wallet addresses list for API request
    const finalWalletAddresses = computed(() => {
      if (walletAddresses.value.length > 0) {
        return walletAddresses.value
      } else {
        return textInput.value.trim() ? [textInput.value.trim()] : []
      }
    })

    // ===== UTILITY FUNCTIONS =====
    
    // Validate Ethereum address format
    const isValidEVMAddress = (address) => {
      const evmRegex = /^0x[a-fA-F0-9]{40}$/
      return evmRegex.test(address)
    }

    // ===== WALLET ADDRESS MANAGEMENT =====
    
    // Add new wallet address to the list
    const addWalletAddress = () => {
      const address = textInput.value.trim()
      addressInputError.value = false
      
      if (!address) return
      
      if (!isValidEVMAddress(address)) {
        addressInputError.value = true
        return
      }
      
      if (!walletAddresses.value.includes(address)) {
        walletAddresses.value.push(address)
        textInput.value = ''
      } else {
        textInput.value = ''
      }
    }

    // Remove wallet address from the list
    const removeWalletAddress = (index) => {
      walletAddresses.value.splice(index, 1)
    }

    // ===== PDF DOWNLOAD FUNCTIONALITY =====
    
    // Handle PDF file download
    const downloadPDF = (blob, filename = 'yam-transactions.pdf') => {
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }

    // ===== MAIN FORM SUBMISSION =====
    
    // Handle form submission and PDF generation
    const handleSubmit = async () => {
      // Trigger validation checks
      dateValidationTriggered.value = true
      
      // Validate form inputs
      if (dateSelectionError.value) {
        return
      }
      
      if (transactionTypes.value.length === 0) {
        return
      }

      if (finalWalletAddresses.value.length === 0) {
        snackbarColor.value = 'error'
        snackbarText.value = 'Please add at least one wallet address'
        snackbar.value = true
        return
      }
      
      loading.value = true
      
      try {
        // Build API request URL using .env variable
        const port = import.meta.env.VITE_API_PORT || '443'
        const origin = window.location.origin
        
        // Remove port from origin (e.g., http://localhost:3000 => http://localhost)
        const domain = origin.replace(/:\d+$/, '')
        
        // If using default HTTPS or HTTP ports, don't add the port in the URL
        const showPort = !['80', '443'].includes(port)
        const apiUrl = `${domain}${showPort ? `:${port}` : ''}/api/generate-report`
        
        // Prepare request payload for API
        const requestBody = {
          start_date: formattedStartDate.value,
          end_date: formattedEndDate.value,
          event_type: transactionTypes.value.map(type => type.toLowerCase()),
          user_addresses: finalWalletAddresses.value,
          display_tx_column: includeTxUrl.value
        }

        // Make API call to generate PDF
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        })

        // Handle API response errors
        if (!response.ok) {
          let errorMessage = 'Failed to generate PDF report'
          try {
            const errorData = await response.json()
            errorMessage = errorData.message || errorData.error || errorMessage
          } catch (e) {
            errorMessage = response.statusText || errorMessage
          }
          
          throw new Error(errorMessage)
        }

        // Process successful response
        const pdfBlob = await response.blob()
        downloadPDF(pdfBlob)
        
        // Show success notification
        snackbarColor.value = 'success'
        snackbarText.value = 'PDF downloaded successfully!'
        snackbar.value = true
        
      } catch (error) {
        console.error('Error generating PDF:', error)
        
        // Show error notification
        snackbarColor.value = 'error'
        snackbarText.value = error.message || 'Failed to generate PDF report'
        snackbar.value = true
        
      } finally {
        loading.value = false
      }
    }

    // ===== COMPONENT EXPORTS =====
    
    return {
      // Form data
      textInput,
      walletAddresses,
      finalWalletAddresses,
      startDate,
      endDate,
      formattedStartDate,
      formattedEndDate,
      transactionTypes,
      includeTxUrl,
      
      // UI state
      loading,
      snackbar,
      snackbarText,
      snackbarColor,
      
      // Validation
      addressInputError,
      transactionTypesError,
      dateSelectionError,
      dateErrorMessage,
      
      // Methods
      addWalletAddress,
      removeWalletAddress,
      handleSubmit
    }
  }
}
</script>

<style scoped>
/* ===== MAIN LAYOUT STYLES ===== */

.hero-section {
  background: linear-gradient(135deg, #d4af37 0%, #b8860b 50%, #8b6914 100%);
  min-height: 100vh;
}

.min-vh-100 {
  min-height: 100vh;
}

/* ===== CARD STYLING ===== */

.glass-card {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(212, 175, 55, 0.4);
  box-shadow: 0 8px 32px rgba(139, 105, 20, 0.3), 
              0 2px 8px rgba(0, 0, 0, 0.1) !important;
}

.switch-card {
  transition: all 0.3s ease;
  border: 2px solid rgb(139, 105, 20) !important;
  background: rgba(139, 105, 20, 0.08);
}

.switch-card-error {
  border: 2px solid #f44336 !important;
  background: rgba(244, 67, 54, 0.08);
}

.switch-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}

.v-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ===== TEXT AND BUTTON STYLING ===== */

.gradient-text {
  background: linear-gradient(45deg, #8b6914, #b8860b, #d4af37);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.action-btn {
  background: linear-gradient(45deg, #8b6914, #b8860b, #d4af37) !important;
  color: white !important;
  transition: all 0.3s ease;
  text-transform: none !important;
  box-shadow: 0 4px 15px rgba(139, 105, 20, 0.4) !important;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(139, 105, 20, 0.5) !important;
}

/* ===== SWITCH ALIGNMENT ===== */

.switch-row {
  width: 100%;
  padding-left: 20px;
}

/* ===== RESPONSIVE DESIGN ===== */

@media (max-width: 600px) {
  .glass-card {
    margin: 1rem;
  }
}
</style>