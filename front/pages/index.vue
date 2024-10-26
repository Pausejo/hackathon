<template>
  <div>
    <h1>Agents configurator</h1>

    <!-- Floating Action Button -->
    <v-btn
      color="primary"
      class="fab-button"
      icon="mdi-plus"
      size="large"
      @click="dialog = true"
    />

    <!-- Create Agent Dialog -->
    <v-dialog v-model="dialog" max-width="500px">
      <v-card>
        <v-card-title>Create New Agent</v-card-title>
        <v-card-text>
          <v-form ref="form">
            <v-textarea
              v-model="newAgent.description"
              label="Description"
              required
            />
            <v-text-field v-model="newAgent.url" label="URL" required />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="error" @click="dialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="createAgent" :loading="loading">
            Create Agent
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useSupabaseClient } from "#imports";

const supabase = useSupabaseClient();
const dialog = ref(false);
const loading = ref(false);
const newAgent = ref({
  description: "",
  url: "",
});

const createAgent = async () => {
  try {
    loading.value = true;
    const { error } = await supabase.from("agents").insert([
      {
        description: newAgent.value.description,
        url: newAgent.value.url,
      },
    ]);

    if (error) throw error;

    // Reset form and close dialog
    dialog.value = false;
    newAgent.value = {
      description: "",
      url: "",
    };
  } catch (error) {
    console.error("Error creating agent:", error);
    // You might want to add error handling/display here
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.fab-button {
  position: fixed;
  bottom: 16px;
  right: 16px;
}
</style>
