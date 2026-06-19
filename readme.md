# Awesome Redis Module [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of resources related to Valkey/Redis modules, including a selection of useful modules.

This project is developed and maintained by the [Resources team][team].

## Contents

- [Libraries](#libraries)
  - [Infrastructure & Utilities](#infrastructure--utilities)
  - [Data Types](#data-types)
  - [Probabilistic Data Structures](#probabilistic-data-structures)
  - [AI & Programmability](#ai--programmability)
  - [Search & Indexing](#search--indexing)
- [SDKs](#sdks)
- [Tools](#tools)
- [Resources](#resources)
- [Contribute](#contribute)

## Libraries

### Infrastructure & Utilities

Rate limiters, authentication modules, consensus protocols, time-series engines, distributed locks, timers, ID generators, and other infrastructure building blocks.


| Repo                                                                                      | Description                                                                                    | Tags         | Status                                            |
| ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------ | ------------------------------------------------- |
| [RedisTimeSeries/RedisTimeSeries](https://github.com/RedisTimeSeries/RedisTimeSeries)     | Time-series data type with downsampling, compaction, and aggregation queries.                  | `timeseries` | 2026-06-17 · Redis Source Available License 2.0   |
| [ayarotsky/redis-shield](https://github.com/ayarotsky/redis-shield)                       | Token-bucket rate limiter with native Valkey/Redis commands, written in Rust.                  | `ratelimit`  | 2026-06-15 · MIT License                          |
| [valkey-io/valkey-ldap](https://github.com/valkey-io/valkey-ldap)                         | LDAP authentication integration for Valkey.                                                    | `auth`       | 2026-05-21 · BSD 3-Clause License                 |
| [brandur/redis-cell](https://github.com/brandur/redis-cell)                               | Single-command rate limiter using the GCRA algorithm.                                          | `ratelimit`  | 2026-02-14 · MIT License                          |
| [tzongw/redis-timer](https://github.com/tzongw/redis-timer)                               | In-process Lua script scheduler supporting periodic and one-shot timers.                       | `utility`    | *2024-05-03* · MIT License                        |
| [chayim/redicrypt](https://github.com/chayim/redicrypt)                                   | Encryption-at-rest module for Redis/Valkey data.                                               | `auth`       | *2023-10-10* · Unknown license                    |
| [RedisLabs/redisraft](https://github.com/RedisLabs/redisraft)                             | Strongly-consistent Redis cluster built on the Raft consensus algorithm.                       | `consensus`  | *2023-07-18* · Redis Source Available License 2.0 |
| [wujunwei/redlock](https://github.com/wujunwei/redlock)                                   | Distributed lock implementation as a Redis module.                                             | `utility`    | *2023-02-19* · MIT License                        |
| [halaei/lqrm](https://github.com/halaei/lqrm)                                             | Laravel-compatible queue driver with server-side millisecond timing and reliable blocking pop. | `utility`    | *2022-01-18* · BSD 3-Clause License               |
| [starkdg/reventis](https://github.com/starkdg/reventis)                                   | Spatio-temporal event indexing, range queries, and object tracking via space-filling curves.   | `timeseries` | *2021-10-31* · Redis Source Available License     |
| [linfangrong/redismodule-ratelimit](https://github.com/linfangrong/redismodule-ratelimit) | Token-bucket rate limiter implemented as a Redis module.                                       | `ratelimit`  | *2020-04-21* · MIT License                        |
| [TamarLabs/ReDe](https://github.com/TamarLabs/ReDe)                                       | Lawn-based data dehydrator managing millions of deferred elements with timed replay.           | `timeseries` | *2020-03-03* · MIT License                        |
| [swilly22/redis-graph](https://github.com/swilly22/redis-graph)                           | Early graph database module for Redis (development moved to RedisGraph main repo).             | `graph`      | *2020-02-13* · GNU GPL                            |
| [f0rmiga/sessiongate](https://github.com/f0rmiga/sessiongate)                             | HTTP session management backed by Redis with pluggable storage backends.                       | `utility`    | *2019-11-11* · MIT License                        |
| [RedisLabsModules/RedisX](https://github.com/RedisLabsModules/RedisX)                     | Native data-type and command extensions (e.g. X.GETSETEX).                                     | `utility`    | *2019-11-01* · Redis Source Available License     |
| [RedisLabsModules/redex](https://github.com/RedisLabsModules/redex)                       | Command-extension collection for Keys, Strings, Hashes, Lists, Sets, ZSets, and Geo.           | `utility`    | *2019-07-25* · GNU GPL                            |
| [limithit/RedisPushIptables](https://github.com/limithit/RedisPushIptables)               | Redis-driven iptables push / linkage security firewall module.                                 | `utility`    | *2019-04-26* · GNU GPL                            |
| [RedisLabsModules/rtexp](https://github.com/RedisLabsModules/rtexp)                       | Fine-grained element expiry management for real-time applications.                             | `utility`    | *2018-12-11* · Apache License                     |
| [danni-m/redis-timeseries](https://github.com/danni-m/redis-timeseries)                   | Early Redis time-series implementation (superseded by RedisTimeSeries).                        | `timeseries` | *2018-09-28* · Apache License                     |
| [itamarhaber/zpop](https://github.com/itamarhaber/zpop)                                   | ZPOP (pop min/max from sorted set) command extension.                                          | `utility`    | *2018-05-17* · Unknown license                    |
| [erans/redissnowflake](https://github.com/erans/redissnowflake)                           | Twitter Snowflake-style 64-bit unique time-ordered ID generation.                              | `id`         | *2017-05-11* · Unknown license                    |
| [RedisLabsModules/password](https://github.com/RedisLabsModules/password)                 | Secure password-hash storage and verification using bcrypt.                                    | `auth`       | *2016-05-18* · GNU GPL                            |
| [RedisLabsModules/graphicsmagick](https://github.com/RedisLabsModules/graphicsmagick)     | Proof-of-concept in-Redis image processing (rotate, etc.) via GraphicsMagick.                  | `utility`    | *2016-05-08* · GNU GPL                            |
| [RedisLabsModules/pam_auth](https://github.com/RedisLabsModules/pam_auth)                 | Proof-of-concept replacing Redis native AUTH with Linux PAM authentication.                    | `auth`       | *2016-05-05* · GNU GPL                            |

### Data Types

Modules that extend Valkey/Redis with new native data types, such as JSON, protobuf, Roaring Bitmaps, interval sets, and enhanced Hash/String/ZSet variants.


| Repo                                                                                    | Description                                                                                    | Tags         | Status                                        |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------ | --------------------------------------------- |
| [valkey-io/valkey-json](https://github.com/valkey-io/valkey-json)                       | Native JSON data type with JSONPath operations for Valkey.                                     | `datatype`   | 2026-06-11 · BSD 3-Clause License             |
| [aviggiano/redis-roaring](https://github.com/aviggiano/redis-roaring)                   | Compressed Roaring Bitmap commands powered by CRoaring.                                        | `datatype`   | 2026-05-08 · MIT License                      |
| [tair-opensource/TairHash](https://github.com/tair-opensource/TairHash)                 | Enhanced Hash with field-level TTL, versioning, and active expiry notifications.               | `tair`       | 2026-01-26 · Apache License                   |
| [tair-opensource/TairGis](https://github.com/tair-opensource/TairGis)                   | R-Tree-based geospatial module with point/line/polygon intersect, contain, and within queries. | `tair` `geo` | 2025-06-05 · Apache License                   |
| [tair-opensource/TairString](https://github.com/tair-opensource/TairString)             | Enhanced String with CAS/CAD, versioning, flags, and memcached protocol support.               | `tair`       | 2024-11-13 · Apache License                   |
| [tair-opensource/TairZset](https://github.com/tair-opensource/TairZset)                 | Enhanced ZSet supporting multi-dimensional (up to 255) score sorting.                          | `tair`       | *2022-12-06* · Apache License                 |
| [ekzhang/redis-rope](https://github.com/ekzhang/redis-rope)                             | High-performance Rope (large string) data type backed by a Splay Tree.                         | `datatype`   | *2022-09-05* · MIT License                    |
| [danitseitlin/redis-interval-sets](https://github.com/danitseitlin/redis-interval-sets) | Interval-set data type for storing and querying numeric ranges.                                | `datatype`   | *2022-06-17* · BSD 3-Clause License           |
| [sewenew/redis-protobuf](https://github.com/sewenew/redis-protobuf)                     | Protobuf messages as a native Redis type with field-level path access.                         | `datatype`   | *2022-06-13* · Apache License                 |
| [OhBonsai/RedisTree](https://github.com/OhBonsai/RedisTree)                             | Polytree (multi-way tree) native data type for hierarchical / organizational data.             | `datatype`   | *2021-07-07* · MIT License                    |
| [RedisJSON/RedisJSON2](https://github.com/RedisJSON/RedisJSON2)                         | JSON as a native Redis data type with JSONPath operations (superseded by RedisJSON).           | `datatype`   | *2020-04-20* · Redis Source Available License |
| [gsquire/redis-multi-map](https://github.com/gsquire/redis-multi-map)                   | Multi-value map (multi-map) data type written in Rust.                                         | `datatype`   | *2019-02-20* · MIT License                    |
| [infobip/redis-fpn](https://github.com/infobip/redis-fpn)                               | Fixed-point-number data type with arithmetic commands for Redis 4.                             | `datatype`   | *2018-08-29* · Apache License                 |

### Probabilistic Data Structures

Memory-efficient approximate data structures including Bloom and Cuckoo filters, Count-Min Sketch, Top-K, t-digest, and Apache DataSketches integration.


| Repo                                                                                  | Description                                                                                         | Tags            | Status                                          |
| ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | --------------- | ----------------------------------------------- |
| [RedisBloom/RedisBloom](https://github.com/RedisBloom/RedisBloom)                     | Probabilistic data structures: Bloom/Cuckoo filters, Count-Min Sketch, Top-K, t-digest.             | `probabilistic` | 2026-06-18 · Redis Source Available License 2.0 |
| [goodform/valkey-datasketches](https://github.com/goodform/valkey-datasketches)       | Apache DataSketches integration providing quantile, frequency, and cardinality sketches for Valkey. | `probabilistic` | 2026-06-11 · BSD 3-Clause License               |
| [valkey-io/valkey-bloom](https://github.com/valkey-io/valkey-bloom)                   | Probabilistic data structures (Bloom/Cuckoo filters, Count-Min Sketch, Top-K) for Valkey.           | `probabilistic` | 2026-06-10 · BSD 3-Clause License               |
| [usmanm/redis-tdigest](https://github.com/usmanm/redis-tdigest)                       | Online quantile and CDF estimation via merging t-digest sketches.                                   | `probabilistic` | *2021-01-14* · MIT License                      |
| [poga/redis-percentile](https://github.com/poga/redis-percentile)                     | Approximate percentile (quantile) statistics module.                                                | `probabilistic` | *2019-12-26* · MIT License                      |
| [RedisLabsModules/topk](https://github.com/RedisLabsModules/topk)                     | Top-K heavy-hitter data structure (superseded by RedisBloom).                                       | `probabilistic` | *2019-07-16* · GNU GPL                          |
| [RedisLabsModules/countminsketch](https://github.com/RedisLabsModules/countminsketch) | Early Count-Min Sketch approximate counting module (superseded by RedisBloom).                      | `probabilistic` | *2019-07-16* · GNU GPL                          |

### AI & Programmability

In-database machine-learning inference, LLM integration, neural-network data types, and programmable scripting engines that run user-defined logic inside Valkey/Redis.


| Repo                                                                  | Description                                                                           | Tags           | Status                                          |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | -------------- | ----------------------------------------------- |
| [valkey-io/valkey-luajit](https://github.com/valkey-io/valkey-luajit) | LuaJIT scripting engine for Valkey with enhanced performance.                         | `programmable` | 2026-06-17 · BSD 3-Clause License               |
| [sewenew/redis-llm](https://github.com/sewenew/redis-llm)             | LLM, prompt, vector store, and conversational / retrieval application integration.    | `ai`           | 2026-05-02 · Apache License                     |
| [RedisGears/RedisGears](https://github.com/RedisGears/RedisGears)     | Programmable execution engine running JavaScript functions and triggers inside Redis. | `programmable` | 2025-08-28 · Redis Source Available License 2.0 |
| [RedisAI/RedisAI](https://github.com/RedisAI/RedisAI)                 | In-Redis deep-learning / ML model inference workload runner (archived).               | `ai`           | 2025-08-20 · Redis Source Available License 2.0 |
| [sklivvz/cthulhu](https://github.com/sklivvz/cthulhu)                 | Embed pre-compiled JavaScript extensions via duktape for custom commands.             | `programmable` | *2019-06-28* · BSD 3-Clause License             |
| [antirez/neural-redis](https://github.com/antirez/neural-redis)       | Feed-forward neural network as a native data type with inline training and inference. | `ai`           | *2018-06-22* · Unknown license                  |

### Search & Indexing

Full-text search, vector similarity search, secondary indexing, and image similarity modules that add query capabilities beyond the built-in Valkey/Redis commands.


| Repo                                                                        | Description                                                                               | Tags     | Status                                          |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | -------- | ----------------------------------------------- |
| [valkey-io/valkey-search](https://github.com/valkey-io/valkey-search)       | Full-text search, vector search, and secondary indexing for Valkey.                       | `search` | 2026-06-18 · BSD 3-Clause License               |
| [RediSearch/RediSearch](https://github.com/RediSearch/RediSearch)           | Secondary index, full-text search, vector search, and aggregation query engine.           | `search` | 2026-06-18 · Redis Source Available License 2.0 |
| [RedisLabsModules/secondary](https://github.com/RedisLabsModules/secondary) | Early secondary index module with SQL-like hash-field queries (superseded by RediSearch). | `search` | *2020-10-19* · GNU GPL                          |
| [starkdg/Redis-ImageScout](https://github.com/starkdg/Redis-ImageScout)     | Perceptual-hash (pHash) image similarity search using MVP-trees.                          | `search` | *2020-10-01* · Redis Source Available License   |
| [zhao-lang/redis_hnsw](https://github.com/zhao-lang/redis_hnsw)             | Approximate nearest-neighbor vector search using the HNSW algorithm.                      | `search` | *2020-09-01* · MIT License                      |

## SDKs

- [valkey-io/libvalkey](https://github.com/valkey-io/libvalkey) - Valkey client library in C.
- [valkey-io/valkey-go](https://github.com/valkey-io/valkey-go) - A fast Golang Valkey client that supports Client Side Caching and Auto Pipelining.
- [valkey-io/valkey-py](https://github.com/valkey-io/valkey-py) - Valkey Python client based on a fork of redis-py.
- [valkey-io/iovalkey](https://github.com/valkey-io/iovalkey) - Valkey client for Node.js, ported from ioredis.
- [valkey-io/jackey](https://github.com/valkey-io/jackey) - Java client for Valkey.

## Tools

- [goodform/valkey-module-template](https://github.com/goodform/valkey-module-template) - Valkey module template to help you quick-start a new module.
- [valkey-io/valkeymodule-rs](https://github.com/valkey-io/valkeymodule-rs) - Rust SDK for writing Valkey modules.

## Resources

- [GoodFORM: Free and Open Redis Modules](https://goodformcode.com/) - Project home page for the GoodFORM initiative.
- [What's in a Module](https://redis.io/community/redis-modules-hub/how-to-build/) - Overview of the Redis module API.
- [How to Write a Redis Module in Zig](https://redis.io/blog/write-redis-module-zig/) - Tutorial on building a Redis module with Zig.
- [5 Steps to Building a Great Redis Module](https://redis.io/blog/5-steps-building-great-redis-module/) - Best-practice checklist when writing a Redis module.

## Contribute

Contributions welcome! Read the [contribution guidelines](contributing.md) first.

[team]: https://github.com/goodform
