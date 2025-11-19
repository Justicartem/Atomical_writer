# atomic_writer

A tiny, easy-to-use Python helper for writing files **atomically**.

Atomic writes mean the file you write is either fully there or not changed at all — no half-written files if the program crashes.

---

## Key features

- `write_atomic(path, data)` accepts `str` or `bytes` and writes safely.
- `write_text_atomic(path, text)` simple helper for text files (UTF-8).
- `write_from_file(dest, source)` copy a file atomically (good for large files).
- `SimpleWriter(path, mode)` context manager for incremental writes.
- `remove_safe(path)` remove a file or empty folder without raising if missing.

---

## Quick start

Copy `atomic_writer.py` into your project and import the functions:

```python
from atomic_writer import write_atomic, write_text_atomic, SimpleWriter, write_from_file, remove_safe
```

### Write text (easy)

```python
write_atomic("hello.txt", "Hello, world with accents: áéíóú")
```

or

```python
write_text_atomic("hello.txt", "Hello, world")
```

### Write bytes

```python
write_atomic("data.bin", b"binary data")
```

### Stream data safely (download, CSV, etc.)

```python
with SimpleWriter("bigfile.bin", mode="wb") as f:
    f.write(chunk1)
    f.write(chunk2)
# file replaces target only if no error occurred
```

### Copy a big file atomically

```python
write_from_file("backup.db", "database.db")
```

### Safe delete

```python
remove_safe("tempfile.tmp")
```

---

## Notes

- The module uses UTF-8 by default for text. You can change encoding if needed.
- `fsync` is used by default to reduce risk of data loss on power failure. Some filesystems behave differently (NFS, network drives).
- If you need to preserve file permissions or owner, set them after writing.


