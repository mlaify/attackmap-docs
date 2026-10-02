# Analyzers

AttackMap's language and framework coverage comes from **analyzer modules**.
Four broad analyzers are built into core. Deeper ecosystem coverage ships as 15
official plugin packages in the [mlaify](https://github.com/mlaify) org. Each
one is a separate repository, versioned on its own and pinned by core.

## Listing what's installed

```bash
attackmap modules            # human-readable, in run order
attackmap modules --json     # name, display_name, description, scope, ecosystems,
                             # enabled_by_default, priority, experimental
```

`attackmap modules` lists only what is installed in the same environment as
`attackmap`. A plugin that isn't installed doesn't run and isn't reported as
missing during `analyze`. Use [`attackmap suggest`](#installing-plugins) to see
which plugins fit a repository.

## Built-in analyzers

These ship with core and are always installed.

| Module | Languages / targets | Priority | Runs | Experimental |
|---|---|---|---|---|
| `python-web` | Python: FastAPI and Flask routes and related security signals | 20 | default | no |
| `javascript-web` | JavaScript / TypeScript (`.js` `.jsx` `.mjs` `.cjs` `.ts` `.tsx`): Express, Fastify, Koa. Fallback; deep Node coverage is in `node-service` | 20 | default | no |
| `config` | YAML / TOML / JSON / INI / `.env` app config: DB connection strings, service URLs, secret-shaped literals | 30 | default | no |
| `default` | Any other code file suffix not claimed by `python-web` or `javascript-web` | 100 | default | no |

## Official plugins

Listed in run order. Priority and the default/opt-in setting come from each
plugin's metadata at the commit pinned in core's plugin lock, as reported by
`attackmap modules --json`. "Known gaps" links to the open issues in each
plugin's repository.

| Module | Package / repo | Languages / targets | Priority | Runs | Experimental | Main signals | Known gaps |
|---|---|---|---|---|---|---|---|
| `python` | [attackmap-analyzer-python](https://github.com/mlaify/attackmap-analyzer-python) | Python: Django, DRF, Starlette, AIOHTTP, Sanic, Litestar, Flask `add_url_rule`. Additive over built-in `python-web` | 15 | default | no | Django/DRF/Starlette/AIOHTTP/Sanic/Litestar routes; SQLAlchemy, asyncpg, psycopg, motor, pymongo, redis, boto3; passlib, bcrypt, argon2, PyJWT, authlib, fastapi-users; httpx/aiohttp calls; `os.environ` and pydantic-settings secrets | [#2](https://github.com/mlaify/attackmap-analyzer-python/issues/2) Django `include()` prefixes, Tornado, Litestar controllers |
| `c` | [attackmap-analyzer-c](https://github.com/mlaify/attackmap-analyzer-c) | C (`.c`, `.h`), CMake/Make projects | 20 | default | yes | civetweb, mongoose, libonion routes; libmicrohttpd entrypoint; libcurl calls; sqlite3, libpq, MySQL, hiredis, mongoc; OpenSSL, mbedTLS, libsodium; `getenv` secrets | [#2](https://github.com/mlaify/attackmap-analyzer-c/issues/2) `.h` ownership vs C++; methods always `ANY` |
| `cpp` | [attackmap-analyzer-cpp](https://github.com/mlaify/attackmap-analyzer-cpp) | C++ (`.cpp` `.cc` `.cxx` `.hpp` …), CMake | 20 | default | yes | Crow, Pistache, Drogon, cpprestsdk routes; libcurl/cpr calls; libpqxx, mongocxx, redis-plus-plus, SOCI; OpenSSL, Botan, libsodium, Crypto++ | [#2](https://github.com/mlaify/attackmap-analyzer-cpp/issues/2) no memory-safety / command-exec sinks yet |
| `dotnet` | [attackmap-analyzer-dotnet](https://github.com/mlaify/attackmap-analyzer-dotnet) | C# / .NET (`.csproj`, `.sln`, `.cs`): ASP.NET Core | 20 | default | no | Minimal APIs and attribute routing; EF Core, Dapper, Npgsql, MongoDB; JwtBearer, OpenIdConnect, Identity, `[Authorize]`; `HttpClient`; configuration secrets | [#2](https://github.com/mlaify/attackmap-analyzer-dotnet/issues/2) route templates, `MapGroup`, per-route auth; no F# or Razor Pages |
| `go` | [attackmap-analyzer-go](https://github.com/mlaify/attackmap-analyzer-go) | Go modules (`go.mod`, `.go`): net/http, chi, gin, echo, fiber, gorilla/mux | 20 | default | no | Routes and entrypoints; `database/sql`, gorm, sqlx, pgx, mongo, go-redis; golang-jwt, oauth2, sessions, casbin, bcrypt; HTTP clients; `os.Getenv`/viper secrets | [#2](https://github.com/mlaify/attackmap-analyzer-go/issues/2) false-positive routes, [#3](https://github.com/mlaify/attackmap-analyzer-go/issues/3) Go 1.22 mux patterns, group prefixes |
| `java-spring` | [attackmap-analyzer-java-spring](https://github.com/mlaify/attackmap-analyzer-java-spring) | Java / Kotlin (Maven, Gradle): Spring MVC/Boot, JAX-RS, Ktor, Javalin, Micronaut | 20 | default | no | Annotation routes with class-level prefixes; Spring Data JPA/Mongo/Redis, JDBC; Spring Security, jjwt, password encoders, OAuth2; RestTemplate, WebClient, Feign; `@Value`/`getenv` secrets | [#2](https://github.com/mlaify/attackmap-analyzer-java-spring/issues/2) bare `@GetMapping`, `path=`; [#3](https://github.com/mlaify/attackmap-analyzer-java-spring/issues/3) WebFlux, `HttpSecurity` rules |
| `omeka-s` | [attack-map-analyzer-omeka-s](https://github.com/mlaify/attack-map-analyzer-omeka-s) (package `attackmap-analyzer-omeka-s`) | PHP: Omeka S and Omeka-style Laminas MVC modules | 20 | opt-in (`-m omeka-s`) | yes | Admin, site and API surfaces; routes and controllers from module config; Omeka services; extension points (navigation, service-manager factories) | [#2](https://github.com/mlaify/attack-map-analyzer-omeka-s/issues/2) ACL rules and API-key auth; costly `detect()` |
| `rust` | [attackmap-analyzer-rust](https://github.com/mlaify/attackmap-analyzer-rust) | Rust crates and workspaces: axum, actix-web, rocket | 20 | default | no | Routes and entrypoints; sqlx, diesel, sea-orm, tokio-postgres, mongodb, redis; jsonwebtoken, argon2/bcrypt, oauth2, axum-login; reqwest, ureq; `std::env::var`/dotenv secrets | [#2](https://github.com/mlaify/attackmap-analyzer-rust/issues/2) nest/scope/mount prefixes; no warp, poem, salvo, tide routes |
| `swift` | [attackmap-analyzer-swift](https://github.com/mlaify/attackmap-analyzer-swift) | Swift: SwiftPM / Xcode projects | 20 | default | yes | SwiftPM detection; `Package.resolved` dependency SBOM (not CVE-matched); Vapor/Hummingbird/Kitura framework hints; `main.swift`/`@main` entrypoints. **No routes yet** | [#1](https://github.com/mlaify/attackmap-analyzer-swift/issues/1) Vapor/Hummingbird routes, app surface (ATS, URL schemes), CocoaPods/Carthage |
| `terraform` | [attackmap-analyzer-terraform](https://github.com/mlaify/attackmap-analyzer-terraform) | Terraform / OpenTofu (`.tf`, `.tf.json`, `.tfvars`): AWS, Azure, GCP | 20 | default | no | Public ingress (open security groups, auth-less Lambda URLs and API Gateway methods, public S3); IAM wildcards; databases; Secrets Manager / SSM / Key Vault and sensitive variables; API Gateway v2 routes | [#2](https://github.com/mlaify/attackmap-analyzer-terraform/issues/2) IAM escalation paths, [#3](https://github.com/mlaify/attackmap-analyzer-terraform/issues/3) egress-as-ingress, policy documents, [#4](https://github.com/mlaify/attackmap-analyzer-terraform/issues/4) module pinning, `for_each` |
| `node-service` | [attackmap-analyzer-node-service](https://github.com/mlaify/attackmap-analyzer-node-service) | Node.js / TypeScript backends and monorepos: Express, Fastify, NestJS, Hono, Koa, Elysia, tRPC, Next.js routes | 25 | opt-in (`-m node-service`) | yes | Service identity; route and handler registration; XRPC handlers; outbound HTTP and env-configured service URLs; datastores; auth/token hints; inter-service and async-worker edges | [#3](https://github.com/mlaify/attackmap-analyzer-node-service/issues/3) false-positive `.get()` routes, [#4](https://github.com/mlaify/attackmap-analyzer-node-service/issues/4) per-route guards, router mounts |
| `php-laminas` | [attackmap-analyzer-php-laminas](https://github.com/mlaify/attackmap-analyzer-php-laminas) | PHP: Laminas / Zend Framework MVC | 30 | opt-in (`-m php-laminas`) | yes | Routes from config arrays; controller and service-manager mappings; outbound calls, datastore, auth and secret hints | [#2](https://github.com/mlaify/attackmap-analyzer-php-laminas/issues/2) `child_routes`, Segment optional parts, latin-1 files |
| `atproto` | [attackmap-analyzer-atproto](https://github.com/mlaify/attackmap-analyzer-atproto) | AT Protocol repos (lexicons, XRPC). An overlay; pair with `node-service` | 35 | opt-in (`-m atproto`) | yes | `com.atproto.*` / `app.bsky.*` namespaces; lexicon-inferred XRPC endpoints; auth, signing and identity hints; event-stream exposure | [#2](https://github.com/mlaify/attackmap-analyzer-atproto/issues/2) query/procedure → GET/POST, record lexicons emitted as routes |
| `iac` | [attackmap-analyzer-iac](https://github.com/mlaify/attackmap-analyzer-iac) | Deployment files: Dockerfile, docker-compose, GitHub Actions, `.env` templates, shell installers. **Not Terraform** (see `terraform`) | 40 | default | no | Dockerfile user, ports, piped `curl` installs, base-image pinning; compose service graph, privileged/host-network/`0.0.0.0` binds; `pull_request_target`, tag-pinned actions; `.env` secret inventory | [#1](https://github.com/mlaify/attackmap-analyzer-iac/issues/1) no Kubernetes/Helm, [#2](https://github.com/mlaify/attackmap-analyzer-iac/issues/2) `Dockerfile.*` names, multi-stage `USER` |
| `php-web` | [attackmap-analyzer-php-web](https://github.com/mlaify/attackmap-analyzer-php-web) | Generic PHP web apps (`composer.json`, `.php`): Laravel-style, Slim-style, attribute routes | 40 | opt-in (`-m php-web`) | yes | Routes; outbound HTTP (`curl_init`, `file_get_contents`, clients); datastore, auth and secret/env hints | [#2](https://github.com/mlaify/attackmap-analyzer-php-web/issues/2) false-positive routes and secrets, [#3](https://github.com/mlaify/attackmap-analyzer-php-web/issues/3) Laravel groups/middleware, Symfony YAML/XML |

"Experimental" means the plugin is heuristic with a higher false-positive
rate. `c`, `cpp` and `swift` are experimental but still run by default at
their current pinned commits; `attackmap modules` notes this.

## Choosing analyzers

Without `--module`, AttackMap runs every installed analyzer whose `detect()`
matches the repository, **except opt-in analyzers**:

```bash
attackmap analyze .
```

Opt-in analyzers (`enabled_by_default=False`, "opt-in" in the tables above)
run only when you name them. When one matches the repo but isn't selected, the
CLI prints a hint on stderr:

```text
Opt-in analyzers match this repo but were not run: node-service. Enable with -m node-service.
```

`--module` (`-m`, repeatable) switches to explicit selection. Only the named
analyzers run, built-ins included only if you name them, and `detect()` still
gates each one:

```bash
attackmap analyze . -m javascript-web -m node-service -m atproto
```

### Run order

Analyzers run in `(priority, name)` order, built-ins and plugins together, so
the tables above are in run order. Results are merged first-seen-wins, so when
two analyzers emit the same signal the one with the lower priority value is
kept. See [How results are merged](sdk.md#how-results-are-merged).

### Failure isolation

If an analyzer raises or returns an invalid result, the scan carries on
without it. The console prints `Analyzer '<name>' failed and was skipped: …`
and `attackmap-report.json` lists it under `scan.analyzer_errors`. Pass
`--strict-analyzers` to fail fast instead, for plugin development and CI.

!!! warning "Version note"
    Opt-in handling and the hint, `(priority, name)` run order, and failure
    isolation (`analyzer_errors`, `--strict-analyzers`) are on core `main` and
    ship in the first release after **v0.4.31**. On v0.4.31 and earlier, every
    installed analyzer whose `detect()` matches runs (`enabled_by_default` and
    `priority` are ignored, built-ins run first), and one failing analyzer
    aborts the scan. See [Feature availability](feature-availability.md).

## Installing plugins

A plain `attackmap analyze` **never installs anything**. If a plugin for your
stack isn't installed, the scan runs without it and reports only what the
installed analyzers found. On a Go repo with no `go` plugin, for example, you
get the generic built-in results.

Ways to get plugins:

- **Ask what fits the repo.** `attackmap suggest .` inspects manifests, file
  extensions and framework markers and prints each recommended plugin that is
  missing, with what matched and its exact pinned `pip install` command.
  `attackmap suggest . --install` then offers to install them (default No; add
  `--yes` for scripts). This is the recommended way.

    ```bash
    attackmap suggest .
    attackmap suggest . --install
    ```

- **Name it with `--module`.** If `-m <name>` names an official plugin that
  isn't installed, AttackMap installs it, pinned to the commit in core's plugin
  lock, only after you confirm at an interactive prompt or when you pass
  `--install-missing`. Otherwise it stops and prints the exact `pip install`
  command. A name that isn't an official plugin is an error and is never
  fetched.

    ```bash
    attackmap analyze . -m go --install-missing
    ```

- **Install everything up front.** The `[all]` extra installs all 15 official
  plugins, each pinned to the commit in core's plugin lock:

    ```bash
    pip install "attackmap[all] @ git+https://github.com/mlaify/AttackMap.git"
    ```

    The Homebrew formula (`brew install mlaify/tap/attackmap`) also installs
    all 15, pinned the same way.

Installs from `suggest --install` and `--module` refuse to `pip install` into a
system (non-virtualenv) Python unless `ATTACKMAP_ALLOW_SYSTEM_INSTALL=1` is
set. Install AttackMap with Homebrew, pipx or a venv so plugins land next to
it. Pinned installs, `--install-missing` and `--trusted-analyzers-only` (load
only official plugins and skip any other package that registers an analyzer)
need v0.4.31 or later; earlier releases installed plugins from each
repository's unpinned default branch.

Want coverage for something not listed? The plugin contract is small. See the
[Analyzer SDK](sdk.md).
