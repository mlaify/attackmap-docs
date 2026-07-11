# Analyzers

AttackMap's language and framework coverage comes from **analyzer modules**.
A few broad analyzers are built in (Python web, JavaScript/TypeScript web,
config files); deeper ecosystem coverage ships as independent plugin packages.

## Listing what's available

```bash
attackmap modules            # human-readable
attackmap modules --json     # machine-readable (name, ecosystems, …)
```

## Choosing analyzers

By default AttackMap runs the analyzers relevant to the languages it detects.
Restrict the run with `--module` (repeatable):

```bash
attackmap analyze . --module python-web --module rust
```

## Auto-install

If a repository needs an official analyzer you don't have installed, AttackMap
fetches it from the mlaify organization on demand — so `attackmap analyze` on a
Go or Spring project pulls the matching plugin the first time it's needed.

## Official ecosystem plugins

Independent packages under the `mlaify` org, e.g.:

- `attackmap-analyzer-python`, `attackmap-analyzer-node-service`
- `attackmap-analyzer-go`, `attackmap-analyzer-rust`
- `attackmap-analyzer-java-spring`, `attackmap-analyzer-dotnet`
- `attackmap-analyzer-c`, `attackmap-analyzer-cpp`
- `attackmap-analyzer-php-web`, `attackmap-analyzer-php-laminas`
- `attackmap-analyzer-iac` (Terraform / IaC), and more.

Install them all up front with `pip install "attackmap[all]"`.

Want coverage for something not listed? The plugin contract is small — see the
[Analyzer SDK](sdk.md).
