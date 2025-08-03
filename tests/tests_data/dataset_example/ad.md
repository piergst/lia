# Which central file contains information about users, groups, and their passwords in AD?

# What is the NTDS.DIT file in AD?

NTDS.DIT is a central file in AD (stored on DCs: C:\Windows\NTDS\). It is the
database that contains information about users, groups, etc. But most
importantly, it contains password hashes for all users in the domain (->
possibility of brute force or pass-the-hash attack). Furthermore, if the Store
password with reversible encryption option is enabled, passwords will be stored
in plaintext...

# What is the SYSVOL folder in AD?

# What does the SYSVOL folder contain in Active Directory?

# Where is the SYSVOL folder located in AD?

# How is the SYSVOL folder used in AD?

# What is the purpose of the SYSVOL folder in a domain?

The SYSVOL folder is a set of files and folders that reside on the local hard disk of each domain controller in a domain and are replicated by the File Replication service (FRS). It contains logon scripts, group policy data, and other domain-wide data.

# How to Uniquely Identify an Object in AD at Different Hierarchical Levels?

# What are "Distinguished Name" and "Relatively Distinguished Name" in AD?

| Term  | Meaning | Example |
|--------|--------------|----------------------------|
| **RDN** | Unique name within a container | `CN=John Doe` |
| **DN** | Fully qualified unique path in the directory | `CN=John Doe,OU=IT,DC=example,DC=com` |

The **RDN** (Relative Distinguished Name) is the unique identifier of an object **within its immediate container**.  
For example, in `CN=John Doe`, `CN` (Common Name) designates the **John Doe** object. This **RDN is unique within its container**, but there may be other **CN=John Doe** objects elsewhere in the directory.

The **DN** (Distinguished Name) is the **fully qualified path** that uniquely identifies an object across the entire directory.  
For example: `CN=John Doe,OU=IT,DC=example,DC=com`.  
This **DN is unique across the entire Active Directory forest**.

---

# What Are the Two Main Identifiers Used for User Authentication in AD?

# What Are "sAMAccountName" and "userPrincipalName" in AD?

In **Active Directory**, `samAccountName` is a **unique identifier** used for authenticating users and computers within a Windows domain.

- It is the **logon name** used with **Windows NT 4.0 and later versions**.  
- It is **limited to a maximum of 20 characters**.  
- It must be **unique within a domain**.  

**Example:**  

- A user **Alice Dupont** may have:  
  - **Full Name (CN)**: `Alice Dupont`  
  - **sAMAccountName**: `adupont`  
  - **UPN (User Principal Name)**: `adupont@example.com`  

📌 **Difference with UPN (`User Principal Name`)**:  

- `sAMAccountName` is a short identifier mainly used for legacy systems.  
- `UPN` follows an email-like format (`user@domain.com`) and is more commonly used today.