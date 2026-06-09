# Lessons Learned

## Mocking

### What to Patch

**router — module import**

```
from app.services import messaging as messaging_service
await messaging_service.send_message(...)   # resolves at call time via the module object

-> patch("app.services.messaging.send_message", new_callable=AsyncMock)
```

**mcp tool — name import**

```
from app.services.contacts import get_phone_number
await get_phone_number(name)                # resolves at call time from the local namespace

-> patch("app.mcp.contacts.get_phone_number", new_callable=AsyncMock)
```

With the module import, messaging_service is a reference to the module object itself. When the router calls messaging_service.send_message, Python looks up send_message on that module object at the moment of the call. Patching app.services.messaging.send_message replaces the attribute on that same module object — so the router sees it.

With the name import, get_phone_number is a direct reference copied into the importing module's namespace at import time. Patching the original in app.services.contacts doesn't affect the copy that already lives in app.mcp.contacts.

The practical takeaway: from module import name → patch where it was imported to. import module as alias → patch where it was defined.
