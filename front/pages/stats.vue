<template>
  <div class="stats-container">
    <div v-for="agent in agents" :key="agent.id" class="agent-stats-card">
      <h3>{{ agent.description }}</h3>
      <div class="stats-info">
        <div class="usage-count">
          <v-icon icon="mdi-counter" class="mr-2" />
          Times Used: {{ agent.usageCount }}
        </div>
        <div class="success-rate">
          <v-icon icon="mdi-check-circle" class="mr-2" />
          Success Rate:
          <span :style="{ color: getSuccessColor(agent.successRate) }">
            {{ agent.successRate }}%
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSupabaseClient } from "#imports";
import type { Database } from "@/types/database.types";

interface Agent {
  id: number;
  description: string;
  usageCount: number;
  successRate: number;
}

const supabase = useSupabaseClient<Database>();
const agents = ref<Agent[]>([]);

// Fetch enabled agents from Supabase
const fetchAgents = async () => {
  const { data, error } = await supabase
    .from("agents")
    .select("id, description, usage_count, success_rate")
    .eq("is_enabled", true);

  if (error) {
    console.error("Error fetching agents:", error);
    return;
  }

  agents.value = data.map((agent) => ({
    id: agent.id,
    description: agent.description,
    usageCount: agent.usage_count || 0,
    successRate: agent.success_rate || 0,
  }));
};

// Fetch agents when component mounts
onMounted(() => {
  fetchAgents();
});

const getSuccessColor = (rate: number): string => {
  // Linear interpolation between red (0%) and green (100%)
  const red = Math.round((1 - rate / 100) * 255);
  const green = Math.round((rate / 100) * 255);
  return `rgb(${red}, ${green}, 0)`;
};
</script>

<style scoped>
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  padding: 1rem;
}

.agent-stats-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stats-info {
  margin-top: 0.5rem;
}

.success-rate,
.usage-count {
  margin: 0.5rem 0;
}
</style>
