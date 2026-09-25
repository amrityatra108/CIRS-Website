/* Progressive discovery controls for the complete CIRS article list. */
(() => {
  const journal = document.querySelector("[data-journal]");
  if (!journal) return;

  const list = journal.querySelector("[data-story-list]");
  const rows = Array.from(list.querySelectorAll("[data-story]"));
  const controls = journal.querySelector("[data-discovery]");
  const topicControls = journal.querySelector("[data-topic-controls]");
  const topics = Array.from(topicControls.querySelectorAll("[data-topic]"));
  const search = journal.querySelector("[data-search-input]");
  const sort = journal.querySelector("[data-sort]");
  const result = journal.querySelector("[data-results]");
  const empty = journal.querySelector("[data-empty]");
  const reset = journal.querySelector("[data-reset]");
  const text = value => String(value || "").normalize("NFKD").toLocaleLowerCase().trim();
  let selectedTopic = "all";

  const originalPosition = row => Number(row.dataset.order);
  const compare = (a, b) => {
    if (sort.value === "title") {
      return a.dataset.title.localeCompare(b.dataset.title) ||
        originalPosition(a) - originalPosition(b);
    }
    const issueDifference = Number(a.dataset.issue) - Number(b.dataset.issue);
    return (sort.value === "oldest" ? issueDifference : -issueDifference) ||
      originalPosition(a) - originalPosition(b);
  };

  function update() {
    const query = text(search.value);
    const searchMatches = rows.filter(row => text(row.dataset.search).includes(query));
    const visible = searchMatches.filter(row =>
      selectedTopic === "all" || row.dataset.category === selectedTopic);

    topics.forEach(button => {
      const topic = button.dataset.topic;
      const count = topic === "all"
        ? searchMatches.length
        : searchMatches.filter(row => row.dataset.category === topic).length;
      button.querySelector("[data-topic-count]").textContent = count;
      button.setAttribute("aria-pressed", String(topic === selectedTopic));
    });

    rows.sort(compare).forEach(row => list.append(row));
    rows.forEach(row => { row.hidden = !visible.includes(row); });
    result.textContent = visible.length === rows.length
      ? rows.length + " stories"
      : visible.length + " of " + rows.length + " stories";
    empty.hidden = visible.length !== 0;
  }

  topics.forEach(button => button.addEventListener("click", () => {
    selectedTopic = button.dataset.topic;
    update();
  }));
  search.addEventListener("input", update);
  sort.addEventListener("change", update);
  reset.addEventListener("click", () => {
    selectedTopic = "all";
    search.value = "";
    sort.value = "newest";
    update();
    search.focus();
  });

  controls.hidden = false;
  topicControls.hidden = false;
  update();
})();
