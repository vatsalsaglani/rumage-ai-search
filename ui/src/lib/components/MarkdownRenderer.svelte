<script>
  import { marked } from "marked";
  export let markdownText = ``;
</script>

<div class="prose prose-invert">
  {@html marked(markdownText)}
</div>
