#ifndef ETHEROS_KERNEL_INTERFACES_LOADER_IF_H
#define ETHEROS_KERNEL_INTERFACES_LOADER_IF_H

/*
 * EtherOS kernel -- minimal plugin load-planning interface (M7 T5).
 *
 * contract stub, not compiled -- userland reference implementation is
 * tools/load_plugins.py.  This header is the machine-readable form of
 * kernel/interfaces/loader-contract.md and MUST NOT be referenced by
 * any build system.
 *
 * Format-agnostic by construction (plan Global Constraint 15, spec 2.2):
 * the kernel only ever sees plugin ids, manifest-declared type tokens,
 * opaque payload references and container policy -- never the concrete
 * structure of any application format.  This header declares the load
 * PLAN only: producing the plan is userland work; real loading at boot
 * (in-image config override + actual load) belongs to a later milestone.
 */

/* ------------------------------------------------------------------ */
/* Identifiers and opaque handles (all format-agnostic)                */
/* ------------------------------------------------------------------ */

/* Plugin identifier: the "name" field of a plugin manifest. */
typedef const char *etheros_plugin_id;

/* Plugin type token: a manifest-declared "type" value, opaque token. */
typedef const char *etheros_plugin_type;

/* Capability identifier: a manifest-declared "capabilities" token. */
typedef const char *etheros_cap_id;

/* Opaque payload reference: points at the payload declared by a plugin
 * manifest.  The kernel never inspects its content or structure. */
typedef const void *etheros_payload_ref;

/* Container policy handle: the manifest-declared "container" object,
 * carried around opaquely; the kernel applies policy, not parses it. */
typedef struct etheros_container_policy *etheros_container_policy_t;

/* Plugin category: directory-based provenance.  Drives the load order
 * and the enablement rule (config is the enablement source for optional). */
typedef enum etheros_category {
    ETHEROS_CATEGORY_BUILTIN = 0, /* plugins/builtin: implicitly enabled */
    ETHEROS_CATEGORY_DEV,         /* plugins/dev: implicitly enabled */
    ETHEROS_CATEGORY_OPTIONAL     /* plugins/optional: enabled iff listed in config */
} etheros_category;

/* Planned isolation level for a loaded plugin (isolation is planned
 * here; the real isolation domain belongs to the routing contract). */
typedef enum etheros_isolation_level {
    ETHEROS_ISOLATION_NONE = 0,
    ETHEROS_ISOLATION_PER_PLUGIN
} etheros_isolation_level;

/* ------------------------------------------------------------------ */
/* Load plan structures                                               */
/* ------------------------------------------------------------------ */

/* Load request: where the enablement config lives and where the plugin
 * tree lives.  Consumes only these two inputs; no inference. */
typedef struct etheros_load_request {
    const char *config_path;  /* [plugins] enabled = enablement source */
    const char *plugins_root; /* root holding the category directories */
} etheros_load_request;

/* One entry of the load plan: everything needed to bind a plugin, and
 * nothing about any application format. */
typedef struct etheros_load_entry {
    etheros_plugin_id          id;           /* manifest "name" */
    etheros_plugin_type        type;         /* manifest "type" */
    etheros_category           category;     /* builtin | dev | optional */
    etheros_payload_ref        payload;      /* opaque ref to manifest "payload" */
    etheros_container_policy_t container;    /* manifest "container", opaque */
    etheros_cap_id            *capabilities; /* manifest "capabilities"; NULL if none */
    etheros_isolation_level    isolation;    /* planned isolation boundary */
} etheros_load_entry;

/* Skipped entry: a plugin present in the tree but not part of the plan. */
typedef struct etheros_skip_entry {
    etheros_plugin_id id;
    const char       *reason;
} etheros_skip_entry;

/* Load plan: the ordered set of entries plus the skipped ones.  The
 * order of "entries" IS the load order.  Since schema v2 a manifest
 * may declare the optional "dependencies" array (ids of the plugins
 * it depends on): the load order is then the dependency TOPOLOGICAL
 * order, a dependency always preceding its dependent.  With no
 * dependency declared the order degenerates to provenance order:
 * builtin, then dev, then optional (lexicographic within each
 * category) -- byte-identical to the pre-v2 output.  A dependency
 * cycle, or a dependency absent from this load's enabled set, is
 * rejected (plan_load returns EINVAL / ENOENT) -- never silently
 * skipped. */
typedef struct etheros_load_plan {
    etheros_load_entry *entries;
    unsigned int        count;
    etheros_skip_entry *skipped;
    unsigned int        skipped_count;
} etheros_load_plan;

/* ------------------------------------------------------------------ */
/* Result codes                                                        */
/* ------------------------------------------------------------------ */

#define ETHEROS_OK     0    /* plan produced */
#define ETHEROS_ENOENT (-1) /* enabled id or dependency matches no manifest */
#define ETHEROS_EINVAL (-2) /* bad manifest, dangling payload, bad dependency */

/* ------------------------------------------------------------------ */
/* Primitive: plan_load                                                */
/*   plan_load(request) -> load_plan                                   */
/*   Resolve the config-declared enabled set against the plugin tree   */
/*   and produce an ordered load plan.  This is a PLANNING primitive:  */
/*   it binds nothing and starts nothing.                              */
/*   Order: dependency topological order (dependency first); with no   */
/*   dependency declared, provenance order.                            */
/*   Unknown enabled id => ETHEROS_ENOENT; missing/invalid manifest    */
/*   or dangling payload reference => ETHEROS_EINVAL (never silently   */
/*   skip an entry the config asked for).  A dependency outside this   */
/*   load's enabled set => ENOENT; a dependency cycle => EINVAL with   */
/*   the cycle members reported.                                       */
/* ------------------------------------------------------------------ */
int etheros_plan_load(const etheros_load_request *request, etheros_load_plan *out_plan);

#endif /* ETHEROS_KERNEL_INTERFACES_LOADER_IF_H */
