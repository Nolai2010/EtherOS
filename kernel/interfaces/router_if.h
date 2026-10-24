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

/* Permission bitmap of an isolation domain (capability boundary).
 * The bit values are the closed set defined by
 * kernel/interfaces/isolation-contract.md §2 (M12). */
typedef unsigned int etheros_perms_t;

/* ------------------------------------------------------------------ */
/* Permission bitmap masks (isolation-contract.md §2: closed set).     */
/* Every bit must be traceable to a manifest-declared capability       */
/* token via the contract §3 mapping table; a token that is not        */
/* listed there maps to no bit at all (default deny).  NET and GUI     */
/* are reserved: no capability token maps to them yet.                 */
/* ------------------------------------------------------------------ */

#define ETHEROS_PERM_NONE     0x00 /* no permission */
#define ETHEROS_PERM_FS_READ  0x01 /* read files */
#define ETHEROS_PERM_FS_WRITE 0x02 /* write files */
#define ETHEROS_PERM_PROC     0x04 /* create/execute a process */
#define ETHEROS_PERM_NET      0x08 /* network access (reserved: no token mapping yet) */
#define ETHEROS_PERM_SYSINFO  0x10 /* read system metrics */
#define ETHEROS_PERM_COMPAT   0x20 /* call the userland translator */
#define ETHEROS_PERM_GUI      0x40 /* graphical interface (reserved: no token mapping yet) */

/* Route query: only consumes the manifest-declared "protocols" and
 * "capabilities" fields; no inference, no heuristics. */
typedef struct etheros_route_query {
    etheros_proto_id protocol;   /* required; NULL => EINVAL */
    etheros_cap_id   capability; /* optional; NULL => protocol-only query */
} etheros_route_query;

/* ------------------------------------------------------------------ */
/* Result codes                                                        */
/* ------------------------------------------------------------------ */

#define ETHEROS_OK         0    /* success */
#define ETHEROS_ENOENT     (-1) /* zero match / unknown plugin or domain */
#define ETHEROS_EAMBIGUOUS (-2) /* multiple plugins declare the queried protocol */
#define ETHEROS_EINVAL     (-3) /* invalid query, dangling payload ref, or bad domain */

/* ------------------------------------------------------------------ */
/* Primitive 1: route                                                  */
/*   route(query) -> plugin_id                                         */
/*   Resolve a protocol/capability query against the set of enabled    */
/*   plugins to EXACTLY ONE plugin.  Zero match => ETHEROS_ENOENT;     */
/*   multiple matches => ETHEROS_EAMBIGUOUS (never silently pick one); */
/*   NULL protocol => ETHEROS_EINVAL.                                  */
/* ------------------------------------------------------------------ */
int etheros_route(const etheros_route_query *query, etheros_plugin_id *out_plugin_id);

/* ------------------------------------------------------------------ */
/* Primitive 2: load                                                   */
/*   load(plugin_id, payload, domain)                                  */
/*   Bind an opaque payload reference into an isolation domain.        */
/*   For compat-bridge plugins the reference is bound ONLY; translation
 *   happens entirely in the userland translator (spec 6 risk 1).      */
/*   Unknown plugin_id => ETHEROS_ENOENT; dangling payload ref or      */
/*   unestablished domain => ETHEROS_EINVAL.                           */
/* ------------------------------------------------------------------ */
int etheros_load(etheros_plugin_id plugin_id, etheros_payload_ref payload, etheros_domain_t domain);

/* ------------------------------------------------------------------ */
/* Primitive 3: isolate                                                */
/*   isolate(domain) -> perms                                          */
/*   Establish an isolation domain and return its permission bitmap;   */
/*   the boundary is capped by manifest-declared capabilities: no bit  */
/*   may exceed what the manifest declared (perms ⊆ declared), and an  */
/*   undeclared capability maps to no bit at all (default deny --      */
/*   isolation-contract.md §2/§3).                                     */
/*   Invalid domain => ETHEROS_EINVAL.                                 */
/* ------------------------------------------------------------------ */
etheros_perms_t etheros_isolate(etheros_domain_t domain);

#endif /* ETHEROS_KERNEL_INTERFACES_ROUTER_IF_H */
