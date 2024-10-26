<template>
  <div>
    <h1>Agents configurator</h1>

    <!-- Agents Grid -->
    <v-container>
      <v-row>
        <v-col
          v-for="agent in agents"
          :key="agent.id"
          cols="12"
          sm="6"
          md="4"
          lg="3"
        >
          <v-card>
            <v-card-title>Agent {{ agent.id }}</v-card-title>
            <v-card-text>
              <p class="text-body-1">{{ agent.description }}</p>
              <v-chip
                class="mt-2"
                color="primary"
                link
                :href="agent.url"
                target="_blank"
              >
                <v-icon start icon="mdi-link" />
                URL
              </v-chip>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

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
import { ref, onMounted } from "vue";
import { useSupabaseClient } from "#imports";
import type { Database } from "~/types/database.types";

const supabase = useSupabaseClient<Database>();
const dialog = ref(false);
const loading = ref(false);
const newAgent = ref({
  description: "",
  url: "",
});
const agents = ref<{ id: string; description: string; url: string }[]>([]);

// Fetch agents on component mount
const fetchAgents = async () => {
  try {
    const { data, error } = await supabase
      .from("agents")
      .select("id, description, url")
      .order("created_at", { ascending: false });

    if (error) throw error;
    agents.value = data;
  } catch (error) {
    console.error("Error fetching agents:", error);
  }
};

// Refetch agents after creating a new one
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
    // Refresh the agents list
    await fetchAgents();
  } catch (error) {
    console.error("Error creating agent:", error);
  } finally {
    loading.value = false;
  }
};

// Fetch agents when component is mounted
onMounted(() => {
  fetchAgents();
});
</script>

<style scoped>
.fab-button {
  position: fixed;
  bottom: 16px;
  right: 16px;
}
</style>
