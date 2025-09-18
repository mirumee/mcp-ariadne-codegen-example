from typing import Annotated, Optional, AsyncGenerator, TypedDict, Any
import tomllib

from fastmcp import Context, FastMCP


from graphql_to_mcp.graphql_client.input_types import (
    ProductOrder,
    ProductWhereInput,
)
from graphql_to_mcp.graphql_client.base_model import BaseModel
from graphql_to_mcp.graphql_client.fragments import Product
from graphql_to_mcp.graphql_client.client import Client


# https://platform.openai.com/docs/mcp
class GPTSearchResult(BaseModel):
    id: str
    title: str
    url: str
    image: Optional[str]

    @classmethod
    def from_product(cls, product: Product) -> "GPTSearchResult":
        return cls(
            id=product.id,
            title=product.name,
            url="https://demo.nimara.store/products/" + product.slug,
            image=product.thumbnail.url,
        )


class GPTSearchResults(TypedDict):
    results: list[GPTSearchResult]

    @classmethod
    def from_products(cls, products: list[Product]) -> "GPTSearchResults":
        return cls(results=[GPTSearchResult.from_product(p) for p in products])


class GPTFetchResult(BaseModel):
    id: str
    title: str
    text: str
    url: str
    metadata: Optional[dict[str, Any]]

    @classmethod
    def from_product(cls, product: Product) -> "GPTSearchResult":
        return cls(
            id=product.id,
            title=product.name,
            text=product.description,
            url="https://demo.nimara.store/products/" + product.slug,
            metadata=product.model_dump(),
        )


# take graphql endpoint from pyproject.toml
graphql_url = tomllib.load(open("pyproject.toml", "rb"))["tool"]["ariadne-codegen"][
    "remote_schema_url"
]
client = Client(url=graphql_url)
mcp = FastMCP("My store MCP Server")
app = mcp.http_app()


async def get_products(
    channel: str,
    where: Optional[ProductWhereInput] = None,
    sort_by: Optional[ProductOrder] = None,
    search_by: Optional[str] = None,
) -> AsyncGenerator[Product, None]:
    """
    Fetch list of products from Saleor GraphQL API.

    We are simplifying API for the MCP server.
    Downloading all products removing pagination.
    Not recommended for catalogues bigger than 1000 products.

    """
    next_cursor = None
    while True:
        data = await client.list_products(
            first=100,
            after=next_cursor,
            channel=channel,
            where=where,
            sort_by=sort_by,
            search=search_by,
        )
        for product_edge in data.products.edges:
            yield Product.model_validate(product_edge.node.model_dump())
        next_cursor = data.products.page_info.end_cursor
        if next_cursor is None:
            break


@mcp.tool(
    annotations={
        "title": "Fetch products",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def products(
    ctx: Context,
    channel: Annotated[
        str,
        """
        Slug of a channel for which the data should be returned. This field is required.
        If the user has not provided it, ask them which channel to use.
        """,
    ],
    where: Annotated[
        ProductWhereInput | None, "Filter products by specific criteria"
    ] = None,
    sortBy: Annotated[ProductOrder | None, "Sort products by specific field"] = None,
    searchBy: Annotated[str | None, "Search products with full-text search"] = None,
) -> list[Product]:
    """Fetch list of products from Saleor GraphQL API.

    This tool retrieves product information such as: ID, name, slug, external reference,
    product type, category, date of creation, date of last update, and pricing.

    Products are channel-aware, meaning that their availability and pricing can vary
    based on the specified channel.
    """
    print("Products")
    where = where.model_dump(exclude_unset=True) if where else None
    sort_by = sortBy.model_dump(exclude_unset=True) if sortBy else None

    try:
        return [
            p
            async for p in get_products(
                channel=channel,
                where=where,
                sort_by=sort_by,
                search_by=searchBy,
            )
        ]
    except Exception as e:
        await ctx.error(str(e))
        raise


@mcp.tool(
    annotations={
        "title": "Get product by ID",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def get_product(
    id: Annotated[str, "ID of a product"],
    channel: Annotated[
        str,
        """
        Slug of a channel for which the data should be returned. This field is required.
        If the user has not provided it, ask them which channel to use.
        """,
    ],
) -> Product:
    """
    Fetch a single product from Saleor by its ID and channel.

    This tool retrieves product information such as: ID, name, slug, external reference,
    product type, category, date of creation, date of last update, and pricing.

    Products are channel-aware, meaning that their availability and pricing can vary
    based on the specified channel.
    """
    print("get product " + id)
    result = await client.product_by_id(id=id, channel=channel)
    return result.product


@mcp.tool(
    annotations={
        "title": "Search products",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def search(
    ctx: Context,
    query: str,
) -> GPTSearchResults:
    """Fetch list of products from Saleor from default channel.

    Don't user it if user requests specific channel.
    """
    print("Search " + query)
    try:
        products = [
            p
            async for p in get_products(
                channel="default-channel",
                search_by=query,
            )
        ]
    except Exception as e:
        await ctx.error(str(e))
        raise
    return GPTSearchResults.from_products(products)


@mcp.tool(
    annotations={
        "title": "Get product by ID",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def fetch(id: str) -> GPTFetchResult:
    """
    Fetch a single product from Saleor default channel.

    Don't user it if user requests specific channel.
    """
    print("Fetch " + id)
    result = await client.product_by_id(id=id, channel="default-channel")
    return GPTFetchResult.from_product(result.product)


def main():
    """
    Main function for project.scripts
    """
    mcp.run(transport="http", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
