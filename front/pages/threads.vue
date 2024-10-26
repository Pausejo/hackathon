<template>
  <v-container>
    <v-row>
      <v-col>
        <h1 class="text-h4 mb-6">Conversation Threads</h1>

        <v-card v-for="thread in threads" :key="thread.id" class="mb-4">
          <v-card-item>
            <template v-slot:title>
              <div class="d-flex justify-space-between align-center">
                <span>{{ thread.reference }}</span>
                <span class="text-caption text-medium-emphasis">{{
                  new Date(thread.created_at).toLocaleString()
                }}</span>
              </div>
            </template>

            <template v-slot:default>
              <v-card class="mt-2" variant="tonal" color="#333">
                <v-card-text>
                  <template v-if="thread.conversation_history?.[0]">
                    <div class="font-weight-medium d-flex align-center">
                      <v-icon class="mr-2">mdi-account</v-icon>
                      {{ thread.conversation_history[0].role }}:
                    </div>
                    <div>{{ thread.conversation_history[0].content }}</div>
                  </template>
                  <div v-else class="text-medium-emphasis font-italic">
                    No messages in conversation
                  </div>
                </v-card-text>
              </v-card>
            </template>
          </v-card-item>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useSupabaseClient } from "#imports";
import type { Database } from "~/types/database.types";

const supabase = useSupabaseClient<Database>();
const threads = ref<Database["public"]["Tables"]["threads"]["Row"][]>([]);

async function fetchThreads() {
  const { data, error } = await supabase
    .from("threads")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) {
    console.error("Error fetching threads:", error);
    return;
  }

  threads.value = data;
}

onMounted(() => {
  fetchThreads();
});
</script>
