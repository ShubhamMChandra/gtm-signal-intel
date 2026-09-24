import { expect, test, type Page } from "@playwright/test"

const MOCK_PROVIDER = {
  name: "Sample AI Cloud Provider",
  short_name: "Sample Provider",
  industry: "AI Infrastructure / Data Center",
  capacity_mw: 1000,
  gpu_count: 20000,
  is_public: false,
  ticker: "",
  hq_location: "Ashburn, VA",
  website: "",
  segment: "Data Center",
}

const MOCK_COMPETITORS = [
  {
    id: 1,
    name: "CoreWeave",
    company_type: "competitor",
    industry: "GPU Cloud / Neocloud",
    website: "https://coreweave.com",
    description: "Leading neocloud.",
    hq_location: "Roseland, NJ",
    employee_count: null,
    is_public: true,
    ticker: "CRWV",
    capacity_mw: 1500,
    gpu_count: 250000,
    known_pricing: null,
    total_funding: null,
    score: null,
    delta: 0,
    segment: "Neocloud",
    signal_count_30d: 2,
    key_customers: ["Microsoft", "OpenAI"],
    strengths: ["Largest independent GPU fleet"],
    weaknesses: ["Customer concentration"],
    threat_level: "high",
    signals: [],
    events: [],
  },
  {
    id: 2,
    name: "Equinix",
    company_type: "competitor",
    industry: "Data Center REIT",
    website: "https://equinix.com",
    description: "Largest data center REIT.",
    hq_location: "Redwood City, CA",
    employee_count: null,
    is_public: true,
    ticker: "EQIX",
    capacity_mw: 3000,
    gpu_count: null,
    known_pricing: null,
    total_funding: null,
    score: null,
    delta: 0,
    segment: "DC REIT",
    signal_count_30d: 0,
    key_customers: [],
    strengths: ["Global interconnection footprint"],
    weaknesses: ["Lower power density per rack"],
    threat_level: "medium",
    signals: [],
    events: [],
  },
]

function landscape(competitors: typeof MOCK_COMPETITORS) {
  return { provider: MOCK_PROVIDER, competitors, segments: [], activity_feed: [] }
}

async function mockApi(page: Page, competitors: typeof MOCK_COMPETITORS, delayMs = 0) {
  await page.route("**/api/compete/landscape", async (route) => {
    if (delayMs) await new Promise((r) => setTimeout(r, delayMs))
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(landscape(competitors)),
    })
  })
  await page.route("**/api/compete/deal-threats", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ threats: [], total_at_risk: 0 }),
    })
  )
}

test.describe("Compete page", () => {
  test("shows the provider row and competitors in the directory (mocked)", async ({ page }) => {
    await mockApi(page, MOCK_COMPETITORS)

    await page.goto("/compete")

    await expect(page.getByRole("heading", { name: "Compete" })).toBeVisible()
    await expect(page.getByText("events this week")).toBeVisible()

    await page.getByRole("tab", { name: /Directory/ }).click()

    await expect(page.getByText("Sample AI Cloud Provider")).toBeVisible()
    await expect(page.getByText("YOU", { exact: true })).toBeVisible()
    await expect(page.getByText("CoreWeave")).toBeVisible()
    await expect(page.getByText("Equinix")).toBeVisible()

    const table = page.locator("table")
    await expect(table).toBeVisible()
    await expect(table.getByRole("row")).toHaveCount(4)
  })

  test("shows the provider row when there are no competitors", async ({ page }) => {
    await mockApi(page, [])

    await page.goto("/compete")

    await expect(page.getByRole("heading", { name: "Compete" })).toBeVisible()
    await page.getByRole("tab", { name: /Directory/ }).click()

    await expect(page.getByText("Sample AI Cloud Provider")).toBeVisible()
    await expect(page.getByText("No competitors match this filter.")).toBeVisible()
  })

  test("shows loading then content", async ({ page }) => {
    await mockApi(page, MOCK_COMPETITORS, 100)

    await page.goto("/compete")

    await expect(page.getByRole("heading", { name: "Compete" })).toBeVisible({ timeout: 15000 })
    await expect(page.getByText("events this week")).toBeVisible({ timeout: 5000 })
  })
})
