<template>
    <div id="app">
        <ChatInterface />
    </div>
</template>

<script setup>
import ChatInterface from '@/components/ChatInterface.vue'
</script>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

#app {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    height: 100vh;
}

body {
    margin: 0;
    padding: 0;
    background: #f5f7fa;
}
</style>