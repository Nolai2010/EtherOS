#ifndef ETHEROS_KERNEL_INTERFACES_ROUTER_IF_H
#define ETHEROS_KERNEL_INTERFACES_ROUTER_IF_H

/*
 * EtherOS kernel -- minimal plugin routing / isolation interface (M3 T3).
 *
 * contract stub, not compiled -- userland reference implementation is
 * tools/route_plugins.py (Task 6).  This header is the machine-readable
 * form of kernel/interfaces/plugin-routing.md and MUST NOT be referenced
 * by any build system.
 *
 * Format-agnostic by construction (plan Global Constraint 15, spec 2.2):
 * the kernel only ever sees protocol identifiers and opaque payload
 * references -- never the concrete structure of any application format.
 * Real kernel routing belongs to a later milestone.
 */

/* ------------------------------------------------------------------ */
/* Identifiers and opaque handles (all format-agnostic)                */
/* ------------------------------------------------------------------ */

/* Protocol identifier: a token declared in a plugin manifest's
 * "protocols" field.  The kernel treats it as an opaque token only. */
typedef const char *etheros_proto_id;

/* Capability identifier: a token declared in a plugin manifest's
 * "capabilities" field (optional route query dimension). */
typedef const char *etheros_cap_id;

/* Plugin identifier: resolved result of a successful route query. */
typedef const char *etheros_plugin_id;

/* Opaque payload reference: points at the payload declared by a plugin
 * manifest.  The kernel never inspects its content or structure. */
typedef const void *etheros_payload_ref;

/* Isolation domain handle. */
typedef struct etheros_domain *etheros_domain_t;

/* Permission bitmap of an isolation domain (capability boundary). */
typedef unsigned int etheros_perms_t;

/* Route query: only consumes the manifest-declared "protocols" and
 * "capabilities" fields; no inference, no heuristics. */
typedef struct etheros_route_query {
    etheros_proto_id protocol;   /* required; NULL => EINVAL */
    etheros_cap_id   capability; /* optional; NULL => protocol-only query */
} etheros_route_query;

/* ------------------------------------------------------------------ */
/* Result codes                                                        */
/* ------------------------------------------------------------------ */

#define ETHEROS_OK           0    /* success */
#define ETHEROS_ENOENT      (-1)  /* zero match / unknown plugin or domain */
#define ETHEROS_EAMBIGUOUS  (-2)  /* multiple plugins declare the queried protocol */
#define ETHEROS_EINVAL      (-3)  /* invalid query, dangling payload ref, or bad domain */

/* ------------------------------------------------------------------ */
/* Primitive 1: route                                                  */
/*   route(query) -> plugin_id                                         */
/*   Resolve a protocol/capability query against the set of enabled    */
/*   plugins to EXACTLY ONE plugin.  Zero match => ETHEROS_ENOENT;     */
/*   multiple matches => ETHEROS_EAMBIGUOUS (never silently pick one); */
/*   NULL protocol => ETHEROS_EINVAL.                                  */
/* ------------------------------------------------------------------ */
int etheros_route(const etheros_route_query *query,
                  etheros_plugin_id *out_plugin_id);

/* ------------------------------------------------------------------ */
/* Primitive 2: load                                                   */
/*   load(plugin_id, payload, domain)                                  */
/*   Bind an opaque payload reference into an isolation domain.        */
/*   For compat-bridge plugins the reference is bound ONLY; translation
 *   happens entirely in the userland translator (spec 6 risk 1).      */
/*   Unknown plugin_id => ETHEROS_ENOENT; dangling payload ref or      */
/*   unestablished domain => ETHEROS_EINVAL.                           */
/* ------------------------------------------------------------------ */
int etheros_load(etheros_plugin_id plugin_id,
                 etheros_payload_ref payload,
                 etheros_domain_t domain);

/* ------------------------------------------------------------------ */
/* Primitive 3: isolate                                                */
/*   isolate(domain) -> perms                                          */
/*   Establish an isolation domain and return its permission bitmap;   */
/*   the boundary is capped by manifest-declared capabilities.         */
/*   Invalid domain => ETHEROS_EINVAL.                                 */
/* ------------------------------------------------------------------ */
etheros_perms_t etheros_isolate(etheros_domain_t domain);

#endif /* ETHEROS_KERNEL_INTERFACES_ROUTER_IF_H */
