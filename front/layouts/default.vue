<template>
  <v-app>
    <v-app-bar>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title>Agents</v-app-bar-title>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer">
      <v-list>
        <v-list-item title="Threads" to="/threads" prepend-icon="mdi-message" />
      </v-list>
      <v-list>
        <v-list-item title="Configurator" to="/" prepend-icon="mdi-cog" />
      </v-list>
      <v-list>
        <v-list-item title="Stats" to="/stats" prepend-icon="mdi-chart-line" />
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-container>
        <slot />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
const drawer = ref(true);
</script>
