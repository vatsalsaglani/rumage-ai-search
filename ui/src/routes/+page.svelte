<script>
  // @ts-nocheck
  import { SvelteToast, toast } from "@zerodevx/svelte-toast";

  import MarkdownRenderer from "$lib/components/MarkdownRenderer.svelte";
  import Spinner from "$lib/components/Spinner.svelte";

  $: input_text = "";
  $: search_processing = false;
  $: search_result = ``;
  $: llm = "anthropic";
  $: plan_search = false;
  $: llms = ["anthropic", "groq"];

  const onSearch = async () => {
    console.log("Search....");
    if (input_text.trim().length === 0) {
      console.error("No text provided");
      return;
    }
    search_result = ``
    search_result += `## Search: ${input_text}\n\n`;
    search_processing = true;
    const response = await fetch(
      // `http://localhost:8899/search?q=${input_text}&llm=groq`
      `http://localhost:8899/plannedSearch?q=${input_text}`
    );
    if (!response.ok) {
      console.error("Response Status: ", response.status);
      search_processing = false;
      toast.push("Search Error! Please try again later", {
        theme: {
          "--toastBackground": "red",
          "--toastColor": "white",
        },
      });
      return;
    }
    const reader = response.body?.getReader();

    const decoder = new TextDecoder("utf-8");

    while (true) {
      const { value, done } = await reader?.read();
      if (done) {
        search_processing = false;

        break;
      }
      search_result += decoder.decode(value, { stream: true });
    }
  };
</script>

<svelte:head>
  <title>Search{input_text.length > 0 ? `: ${input_text}` : ``}</title>
</svelte:head>
<div class="min-h-screen bg-gray-800">
  <div class="flex flex-col justify-start py-8 items-center min-h-screen">
    <div class="text-3xl font-bold text-gray-200 mb-4">
      Search for Knowledge
    </div>
    <div
      class="w-1/2 flex flex-col justify-center-items-center border-2 border-gray-100 rounded-lg px-2 py-3"
    >
      <textarea
        placeholder="Search..."
        bind:value={input_text}
        class="px-2 py-1 h-2/5 min-w-full overflow-auto resize-none text-gray-300 focus:ring-0 focus:border-0 focus:outline-none bg-transparent"
      ></textarea>
      <div class="flex flex-row-reverse justify-between space-x-2">
        <div class="flex space-x-1">
          <button
            class="rounded-full bg-sky-600 hover:bg-sky-500 p-2 text-gray-100 font-bold"
            on:click={onSearch}
          >
            {#if search_processing}
              <Spinner />
            {:else}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-6 h-6"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M17.25 8.25 21 12m0 0-3.75 3.75M21 12H3"
                />
              </svg>
            {/if}
          </button>
        </div>
      </div>
    </div>
    <!-- {#if search_result.length === 0}
    {/if} -->
    <div class="my-4 p-3 max-h-[70vh] overflow-y-auto">
      {#if search_result.length > 0}
        <MarkdownRenderer markdownText={search_result} />
      {/if}
    </div>
  </div>
</div>
<SvelteToast options={{ reversed: true, intro: { y: 192 } }} />
