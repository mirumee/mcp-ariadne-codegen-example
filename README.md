# From GraphQL Schema to AI-Ready MCP Server in Minutes

Every business is racing to make data usable by AI assistants like ChatGPT, Claude, or Perplexity. The challenge? Your data sits behind APIs too complex for non-developers. Training an LLM to speak your API’s language is costly and unreliable. That’s where **MCP servers (Model Context Protocol)** step in.

This repo shows how to take a **GraphQL schema** and turn it into a fully functional **MCP server** using [Ariadne Codegen](https://ariadnegraphql.org/client/intro) and [FastMCP](https://fastmcp.com). The result: structured, type-safe tools your AI assistant can call directly.

## Why This Matters

- APIs are too complex for non-developers.
- Training LLMs to use APIs is error-prone and expensive.
- MCP servers bridge the gap: you expose tools, not docs.

**Example query from ChatGPT → API call**:

> _"Show me women’s shoes under 100 PLN available in the Polish channel"_

This becomes a validated GraphQL query executed against your backend, **no custom UI required**.

## What Is MCP?

MCP servers are the new extension surface for AI assistants.
They let you expose your existing APIs as tools:

- No plugin marketplace friction.
- No extra UI.
- Just direct access for AI.

For **e-commerce, SaaS, or any data-driven business**, this means product discovery, catalog browsing, and customer support become instantly AI-ready.

## Our Stack

- **GraphQL** – schema-first, typed APIs
- **Ariadne Codegen** – generates async GraphQL clients + Pydantic models
- **FastMCP** – framework for MCP server hosting & tool exposure

## Running locally

```bash
git clone https://github.com/mirumee/mcp-ariadne-codegen-example
cd mcp-ariadne-codegen-example
python -m venv .venv
source .venv/bin/activate
pip install -e .
mcp

```

## Testing With Postman

Postman now supports MCP requests natively.
You can call endpoints, inspect request/response, and validate before exposing them to ChatGPT.
See [Postman MCP docs](https://learning.postman.com/docs/mcp/overview/) for details.

## Case Study: Saleor E-Commerce API

We implemented this demo using [Saleor](https://saleor.io), a headless e-commerce platform with a rich GraphQL API.
Focus area: the `products` query — complex filters, search, ordering, and cursor pagination.

Instead of teaching ChatGPT cursor-based pagination, we **wrapped Saleor GraphQL** with Ariadne Codegen + FastMCP. The assistant can now call typed tools directly.

Demo storefront: [nimara.store](https://nimara.store).
