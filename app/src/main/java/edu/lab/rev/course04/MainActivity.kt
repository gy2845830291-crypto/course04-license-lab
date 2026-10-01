package edu.lab.rev.course04

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val input = findViewById<EditText>(R.id.keyInput)
        val go = findViewById<Button>(R.id.checkButton)
        val out = findViewById<TextView>(R.id.resultText)

        go.setOnClickListener {
            val k = input.text.toString()
            // 单一判定分支，patch 练习就打这里
            if (LicenseCheck.isValidKey(k)) {
                val lic = LicenseCheck.parseKey(k)
                out.text = getString(R.string.lic_ok, lic?.userId, lic?.expiryDays)
            } else {
                out.text = getString(R.string.lic_bad)
            }
        }
    }
}
