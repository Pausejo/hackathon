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
          <v-card
            :class="{
              'disabled-card': !agent.is_enabled,
            }"
          >
            <v-card-title class="d-flex justify-space-between align-center">
              <span>Agent</span>
              <v-switch
                v-model="agent.is_enabled"
                :loading="agent.updating"
                density="compact"
                color="primary"
                hide-details
                @update:model-value="toggleAgent(agent)"
              />
            </v-card-title>
            <v-card-text>
              <p class="text-body-1 text-grey">{{ agent.description }}</p>
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
const agents = ref<
  {
    id: string;
    description: string;
    url: string;
    is_enabled: boolean;
    updating?: boolean;
  }[]
>([]);

// Update the agents type to include is_enabled
const toggleAgent = async (agent: any) => {
  try {
    // Set local loading state for this specific agent
    agent.updating = true;

    const { error } = await supabase
      .from("agents")
      .update({ is_enabled: agent.is_enabled })
      .eq("id", agent.id);

    if (error) {
      // Revert the switch if there's an error
      agent.is_enabled = !agent.is_enabled;
      throw error;
    }
  } catch (error) {
    console.error("Error updating agent:", error);
    // You might want to show an error notification here
  } finally {
    agent.updating = false;
  }
};

// Update fetchAgents to include is_enabled
const fetchAgents = async () => {
  try {
    const { data, error } = await supabase
      .from("agents")
      .select("id, description, url, is_enabled")
      .order("created_at", { ascending: false });

    if (error) throw error;
    agents.value = data.map((agent) => ({
      ...agent,
      updating: false, // Add updating property for loading state
    }));
  } catch (error) {
    console.error("Error fetching agents:", error);
  }
};

// Update createAgent to include is_enabled
const createAgent = async () => {
  try {
    loading.value = true;
    const { error } = await supabase.from("agents").insert([
      {
        description: newAgent.value.description,
        url: newAgent.value.url,
        is_enabled: true, // Set default value for new agents
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
.disabled-card {
  background: repeating-linear-gradient(
    45deg,
    rgb(245, 245, 245),
    rgb(245, 245, 245) 10px,
    rgb(240, 240, 240) 10px,
    rgb(240, 240, 240) 20px
  ) !important;
}
</style>
