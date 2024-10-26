<template>
  <v-app>
    <v-app-bar>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title>Agents configurator</v-app-bar-title>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer">
      <v-list>
        <v-list-item title="Home" to="/" prepend-icon="mdi-home" />
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
