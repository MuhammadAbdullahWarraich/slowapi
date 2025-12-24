# slowapi
TODOS:
- test DI system for:
    - async function having sync generator as a dependency
    - sync function having async generator as a dependency
    - unnamed callables(like object of fastapi.security.OAuth2PasswordBearer class)
    - remove depends-related metadata from signature(aesthetic stuff; won't matter to user of framework, but quality matters)