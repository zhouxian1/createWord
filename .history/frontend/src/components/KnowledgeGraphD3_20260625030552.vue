<template>
  <div ref="containerRef" class="graph-stage"></div>
</template>

<script setup>
import * as d3 from 'd3'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  graph: {
    type: Object,
    default: () => ({ nodes: [], links: [] })
  },
  height: {
    type: Number,
    default: 420
  }
})

const containerRef = ref(null)
let cleanup = null

const palette = {
  document: '#00f0ff',
  chapter: '#39ff14',
  code_entity: '#ff8c00',
  term: '#ff2d95',
  unknown: '#b44dff'
}

const renderGraph = () => {
  if (!containerRef.value) return
  containerRef.value.innerHTML = ''
  if (!props.graph?.nodes?.length) return

  const width = containerRef.value.clientWidth || 520
  const height = props.height
  const nodes = props.graph.nodes.map(item => ({ ...item }))
  const links = props.graph.links.map(item => ({ ...item }))

  const svg = d3.create('svg')
    .attr('viewBox', `0 0 ${width} ${height}`)
    .attr('class', 'graph-svg')

  const defs = svg.append('defs')
  const marker = defs.append('marker')
    .attr('id', 'graph-arrow')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 18)
    .attr('refY', 0)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
  marker.append('path')
    .attr('fill', '#00f0ff')
    .attr('d', 'M0,-5L10,0L0,5')

  const root = svg.append('g')

  const zoom = d3.zoom()
    .scaleExtent([0.45, 2.5])
    .on('zoom', event => root.attr('transform', event.transform))

  svg.call(zoom)

  const link = root.append('g')
    .attr('stroke', '#00f0ff')
    .attr('stroke-opacity', 0.25)
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('stroke-width', 1.2)
    .attr('marker-end', 'url(#graph-arrow)')

  const linkLabel = root.append('g')
    .selectAll('text')
    .data(links)
    .join('text')
    .attr('fill', '#6b8aad')
    .attr('font-size', 9)
    .attr('font-family', 'Share Tech Mono, Consolas, monospace')
    .attr('text-anchor', 'middle')
    .text(item => item.label || item.value || '')

  const node = root.append('g')
    .selectAll('g')
    .data(nodes)
    .join('g')
    .style('cursor', 'grab')

  node.append('circle')
    .attr('r', item => item.type === 'document' ? 18 : item.type === 'chapter' ? 14 : 11)
    .attr('fill', item => palette[item.type] || palette.unknown)
    .attr('fill-opacity', 0.95)
    .attr('stroke', '#d7e6ff')
    .attr('stroke-width', 1.4)

  node.append('text')
    .attr('dy', item => item.type === 'document' ? 34 : 28)
    .attr('text-anchor', 'middle')
    .attr('fill', '#eaf4ff')
    .attr('font-size', 11)
    .text(item => {
      const text = item.name || item.id
      return text.length > 14 ? `${text.slice(0, 14)}...` : text
    })

  node.append('title')
    .text(item => `${item.name || item.id}\n${item.type || 'unknown'}\n${item.value || ''}`)

  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(item => item.id).distance(110))
    .force('charge', d3.forceManyBody().strength(-340))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(item => item.type === 'document' ? 28 : 20))

  const drag = d3.drag()
    .on('start', (event, item) => {
      if (!event.active) simulation.alphaTarget(0.25).restart()
      item.fx = item.x
      item.fy = item.y
    })
    .on('drag', (event, item) => {
      item.fx = event.x
      item.fy = event.y
    })
    .on('end', (event, item) => {
      if (!event.active) simulation.alphaTarget(0)
      item.fx = null
      item.fy = null
    })

  node.call(drag)

  simulation.on('tick', () => {
    link
      .attr('x1', item => item.source.x)
      .attr('y1', item => item.source.y)
      .attr('x2', item => item.target.x)
      .attr('y2', item => item.target.y)

    linkLabel
      .attr('x', item => (item.source.x + item.target.x) / 2)
      .attr('y', item => (item.source.y + item.target.y) / 2 - 6)

    node.attr('transform', item => `translate(${item.x},${item.y})`)
  })

  containerRef.value.appendChild(svg.node())
  cleanup = () => simulation.stop()
}

watch(() => props.graph, renderGraph, { deep: true })
watch(() => props.height, renderGraph)

onMounted(renderGraph)
onBeforeUnmount(() => {
  if (cleanup) cleanup()
})
</script>

<style scoped>
.graph-stage {
  width: 100%;
  min-height: 280px;
  border-radius: 18px;
  overflow: hidden;
  background:
    radial-gradient(circle at 20% 20%, rgba(77, 180, 255, 0.18), transparent 30%),
    radial-gradient(circle at 80% 30%, rgba(95, 240, 194, 0.14), transparent 26%),
    linear-gradient(180deg, rgba(8, 16, 34, 0.96), rgba(6, 10, 24, 0.98));
  border: 1px solid rgba(110, 168, 255, 0.18);
}

.graph-stage :deep(.graph-svg) {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
