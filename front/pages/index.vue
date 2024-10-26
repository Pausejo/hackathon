<template>
  <div>
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
              <span>Agent {{ agent.id }}</span>
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
                v-for="action in agent.actions"
                class="mt-2 mr-2"
                color="primary"
                link
                :href="action.type === 'URL' ? action.action : undefined"
                target="_blank"
              >
                <v-tooltip activator="parent" location="top">
                  {{ action.action }}
                </v-tooltip>
                <v-icon
                  start
                  :icon="action.type === 'URL' ? 'mdi-link' : 'mdi-database'"
                />
                {{ action.type }}
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
    <v-dialog v-model="dialog" max-width="700px">
      <v-card>
        <v-card-title>Create New Agent</v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="formValid">
            <v-textarea
              v-model="newAgent.description"
              label="Description"
              :rules="[(v) => !!v || 'Description is required']"
              required
            />

            <!-- New Actions Section -->
            <div class="actions-section">
              <div class="d-flex justify-space-between align-center mb-3">
                <h3 class="text-h6">Actions</h3>
                <v-btn
                  color="primary"
                  size="small"
                  @click="addAction"
                  icon="mdi-plus"
                />
              </div>

              <div
                v-for="(action, index) in newAgent.actions"
                :key="index"
                class="action-item mb-4"
              >
                <div class="d-flex align-start gap-2">
                  <v-select
                    v-model="action.type"
                    :items="['URL', 'DB']"
                    label="Type"
                    required
                    density="compact"
                    style="width: 25%"
                  />
                  <v-text-field
                    v-model="action.action"
                    label="Action"
                    density="compact"
                    required
                    style="width: 75%"
                  />
                  <v-btn
                    class="ml-2"
                    color="error"
                    icon="mdi-delete"
                    size="small"
                    @click="removeAction(index)"
                  />
                </div>
              </div>
            </div>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="error" @click="dialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            @click="createAgent"
            :loading="loading"
            :disabled="!formValid"
          >
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
  actions: [] as { type: string; action: string }[],
});
const agents = ref<
  {
    id: string;
    description: string;
    is_enabled: boolean;
    actions: { type: string; action: string }[];
    updating?: boolean;
  }[]
>([]);

const form = ref<any>(null);
const formValid = ref(false);

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
      .select(
        `
        id, 
        description, 
        is_enabled,
        agent_actions (
          action:actions(id, type, action)
        )
      `
      )
      .order("created_at", { ascending: false });

    if (error) throw error;
    agents.value = data.map((agent) => ({
      ...agent,
      actions: agent.agent_actions.map((aa) => ({
        type: aa.action.type,
        action: aa.action.action,
      })),
      updating: false, // Add updating property for loading state
    }));
  } catch (error) {
    console.error("Error fetching agents:", error);
  }
};

// Add new helper functions
const addAction = () => {
  newAgent.value.actions.push({ type: "URL", action: "" });
};

const removeAction = (index: number) => {
  newAgent.value.actions.splice(index, 1);
};

// Update createAgent function
const createAgent = async () => {
  try {
    const { valid } = await form.value.validate();
    if (!valid) return;

    loading.value = true;

    // First create the agent
    const { data: agentData, error: agentError } = await supabase
      .from("agents")
      .insert([
        {
          description: newAgent.value.description,
          is_enabled: true,
        },
      ])
      .select();

    if (agentError) throw agentError;

    // Then create all actions
    const actionsPromises = newAgent.value.actions.map(async (action) => {
      // Create action
      const { data: actionData, error: actionError } = await supabase
        .from("actions")
        .insert([
          {
            type: action.type,
            action: action.action,
          },
        ])
        .select();

      if (actionError) throw actionError;

      // Create agent_action relationship
      const { error: relationError } = await supabase
        .from("agent_actions")
        .insert([
          {
            agent_id: agentData[0].id,
            action_id: actionData[0].id,
          },
        ]);

      if (relationError) throw relationError;
    });

    await Promise.all(actionsPromises);

    // Reset form and close dialog
    dialog.value = false;
    newAgent.value = {
      description: "",
      actions: [],
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
