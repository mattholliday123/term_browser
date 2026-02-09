import re
import time
import requests 
import json
from bs4 import BeautifulSoup
from textual.app import App, ComposeResult
from textual.widgets import Static, Button, Input, Label, Tabs, Markdown, ContentSwitcher, Tab
from textual.containers import Container, Horizontal,ScrollableContainer, VerticalScroll, Vertical
from textual import work
from textual import on
from client import send_message

class MyApp(App):
    CSS_PATH = "app.tcss"
    BINDINGS = [ 
                ("escape", "normal_mode", "Enter Normal Mode"),
                ("i", "insert_mode", "Enter Insert Mode")
                ]

    def compose(self) -> ComposeResult:
        yield Tabs(Tab("Search", id="home_view_tab"),id="tabs_bar", active="home_view_tab")
        with ContentSwitcher(id="main_switcher", initial="home_view"):
            with Vertical(id="home_view"):
                yield Static("Koudelka", classes = "title")
                yield Horizontal(
                Input(placeholder = "search...", id="search_bar"),
                classes = "search_bar",
                )
                yield Container(id="results")
                yield Static("--Normal--", id="indicator")
            

    def on_mount(self) -> None:
        search_bar = self.query_one("#search_bar", Input)
        search_bar.disabled=True
        search_bar.can_focus = False


    @work(thread=True)
    def perform_search(self, query: str):
        return json.loads(send_message(query).strip())

    #runs when use searches query
    @on(Input.Submitted)
    async def get_search(self):
        input = self.query_one(Input)
        query = input.value
        self.query_start_time = time.perf_counter()
        input.value = ""
        self.query_one("#main_switcher").current = "home_view"
        self.query_one("#tabs_bar").active = "home_view_tab" 
        results_container = self.query_one("#results")
        results_container.remove_children()
        results_container.mount(Label(f"search results for {query}"))
        try:
            worker = self.perform_search(query)
            results = await worker.wait()
            elapsed = time.perf_counter() - self.query_start_time
            results_container.mount(Label(f"elapsed: {elapsed * 1000:.2f}ms"))
            for res in results:
                button = Button(res['title'], classes="result_link")
                button.data = {"url": res['link'], "title": res['title']}
                results_container.mount(button)
                #results_container.mount(Static(res['link'], classes="link_url"))
        except Exception as e:
            results_container.mount(Label(f"Error: {e}", variant="error"))

    @on(Button.Pressed, ".result_link")
    def handle_click(self, event: Button.Pressed):
        switcher = self.query_one("#main_switcher")
        tabs_bar = self.query_one("#tabs_bar")
        url = event.button.data["url"]
        title = event.button.data["title"]
        page_id = f"page_{hash(url)}" 

        if not self.query(f"#{page_id}"):
            # Create the tab
            tabs_bar.add_tab(Tab(title, id=page_id))
            content = self._fetch_clean_text(url)
            new_page = VerticalScroll(
                Markdown(content),
                id=page_id
            )
            switcher.mount(new_page)

        switcher.current = page_id
        tabs_bar.active = page_id

    @on(Tabs.TabActivated)
    def handle_tab_switch(self, event: Tabs.TabActivated):
        """Switches the content when the user clicks a tab"""
        if event.tab:
            if event.tab.id == "home_view_tab":
                self.query_one("#main_switcher").current = "home_view"
            else:
                self.query_one("#main_switcher").current = event.tab.id

    #try to make the body text look cleaner
    def _fetch_clean_text(self, url: str) -> str:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")

            # Remove clutter
            for tag in ['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript', 'ad']:
                for match in soup.find_all(tag):
                    match.decompose()

            # Target main content
            main_content = soup.select_one('article') or soup.select_one('main') or soup.select_one('.content') or soup.body or soup
            for h in main_content.find_all(['h1', 'h2', 'h3']):
                h.string = f"\n# {h.get_text()}\n"
            if not main_content:
                main_content = soup.body or soup

            text = main_content.get_text(separator='\n', strip=True)
            text = re.sub(r'\n{3,}', '\n\n', text)
            lines = [line.strip() for line in text.split('\n')]
            clean_text = '\n'.join([l for l in lines if l])
            page_title = soup.title.string if soup.title else "Untitled Page"
            return f"# {page_title}\n\n---\n\n{clean_text}"
        except Exception as e:
            return f"### Failed to load page\n{str(e)}"    

    #defines normal mode
    def action_normal_mode(self) -> None:
        indicator = self.query_one("#indicator", Static)
        search_bar = self.query_one("#search_bar", Input)
        indicator.update("--Normal--")
        indicator.remove_class("insert")
        indicator.add_class("normal")
        search_bar.disabled=True
        search_bar.can_focus = False
        self.set_focus(None)

    #defines insert mode
    def action_insert_mode(self) -> None:
        indicator = self.query_one("#indicator", Static)
        search_bar = self.query_one("#search_bar", Input)
        indicator.update("--Insert--")
        indicator.remove_class("normal")
        indicator.add_class("insert")
        search_bar.disabled=False
        search_bar.can_focus = True 
        search_bar.focus()
        

if __name__ == "__main__": 
    app = MyApp()
    app.run()
